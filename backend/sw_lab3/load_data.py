"""Отримання відомостей про українські фільми з Wikidata та їх доповнення даними TMDb"""
import json
import os
import time
import re
from difflib import SequenceMatcher
import dotenv
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

dotenv.load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p"

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "UkrainianCinemaProject/1.0"

OUTPUT_FILE = "movies.json"

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json",
}

WIKIDATA_QUERY = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?film ?filmLabel (MIN(?date) AS ?releaseDate)
       (SAMPLE(?duration) AS ?wikidataDuration)
WHERE {
    ?film wdt:P31 wd:Q11424 ;
          wdt:P495 wd:Q212 .

    OPTIONAL { ?film wdt:P577 ?date . }
    OPTIONAL { ?film wdt:P2047 ?duration . }

    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "uk,en".
    }
}
GROUP BY ?film ?filmLabel
"""

def get_wikidata_films():
    """Отримує унікальні записи про фільми з Wikidata за допомогою SPARQL.
    Повторює запит у разі помилки та повертає список фільмів
    """
    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT)
    sparql.setQuery(WIKIDATA_QUERY)
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    sparql.setTimeout(120)
    sparql.addCustomHttpHeader("User-Agent", USER_AGENT)

    for attempt in range(1, 5):
        try:
            results = sparql.query().convert()
            films = []
            for row in results["results"]["bindings"]:
                release_date = row.get("releaseDate", {}).get("value", "")
                wikidata_duration = row.get("wikidataDuration", {}).get("value", "")
                films.append({
                    "film": row["film"]["value"],
                    "filmLabel": row.get("filmLabel", {}).get("value", ""),
                    "year": release_date[:4] if release_date else "",
                    "wikidataDuration": wikidata_duration,
                })

            unique_films = {film["film"]: film for film in films}
            return list(unique_films.values())

        except Exception as e:
            print(f"Wikidata: спроба {attempt}/4 невдала: {e}")
            if attempt == 4:
                raise
            time.sleep(5 * attempt)

    return []

def normalize_title(title):
    """Нормалізує назву фільму: прибирає розділові знаки, зайві пробіли та змінює регістр"""
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", " ", title)
    return " ".join(title.split())


def title_similarity(title1, title2):
    """Обчислює подібність нормалізованих назв фільмів за шкалою від 0 до 1"""
    return SequenceMatcher(
        None,
        normalize_title(title1),
        normalize_title(title2),
    ).ratio()

def image_url(path, size="w500"):
    """Формує URL зображення TMDb заданого розміру або повертає порожній рядок"""
    if not path:
        return ""
    return f"{TMDB_IMAGE_URL}/{size}{path}"

def is_wikidata_id(title):
    """Перевіряє, чи є переданий рядок ідентифікатором Wikidata формату Q та цифри"""
    return bool(re.fullmatch(r"Q\d+", title or ""))

def years_close(year1, year2, tolerance=1):
    """Перевіряє, чи різниця між роками не перевищує допустиму межу"""
    try:
        return abs(int(year1) - int(year2)) <= tolerance
    except (TypeError, ValueError):
        return True

def parse_duration(value):
    """Перетворює тривалість на цілу кількість хвилин."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    if number > 600:
        number /= 60
    return round(number)


def tmdb_request(endpoint, params=None, retries=3):
    """Виконує авторизований GET-запит до API TMDb
    При статусі 429 повторює запит, якщо залишилися спроби.
    """
    for attempt in range(1, retries + 1):
        response = requests.get(
            f"{TMDB_API_URL}/{endpoint}",
            headers=HEADERS,
            params=params or {},
            timeout=30,
        )

        if response.status_code == 429 and attempt < retries:
            wait = int(response.headers.get("Retry-After", 2))
            print(f"TMDb: забагато запитів, {wait} с")
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response.json()
    return {}

def find_tmdb_movie(title, year=""):
    """Шукає найкращий збіг фільму в TMDb за назвою та роком випуску.
    Порівнює нормалізовані назви й відкидає збіги з оцінкою нижче 0.35.
    Args:
        title: Назва фільму.
        year: Необов’язковий рік випуску.
    Returns:
        Запис найкращого кандидата або None, якщо збіг не знайдено.
    """
    if not title:
        return None

    params = {
        "query": title,
        "language": "uk-UA",
        "include_adult": False,
    }

    if year:
        params["year"] = year

    try:
        data = tmdb_request("search/movie", params)
        results = data.get("results", [])

        if not results and year:
            params.pop("year", None)
            data = tmdb_request("search/movie", params)
            results = data.get("results", [])

        if not results:
            return None

        candidates = []

        for item in results:
            tmdb_year = item.get("release_date", "")[:4]

            if year and tmdb_year and not years_close(year, tmdb_year):
                continue

            score = max(title_similarity(title, item.get("title", "")), title_similarity(title, item.get("original_title", "")),)
            candidates.append((score, item))

        if not candidates:
            return None

        candidates.sort(key=lambda candidate: candidate[0], reverse=True)
        best_score, best_match = candidates[0]

        if best_score < 0.35:
            print(f"Сумнівний збіг: {title} - {best_match.get('title')}")
            return None

        return best_match

    except requests.RequestException as e:
        print(f"Помилка пошуку TMDb для «{title}»: {e}")
        return None

def people_by_jobs(crew, jobs=(), department=None, keywords=()):
    """Відбирає унікальних учасників знімальної групи
    Args:
        crew: Список учасників знімальної групи з TMDb
        jobs: Точні назви професій
        department: Необов’язкова назва відділу
        keywords: Ключові слова у назві професії для заданого відділу
    Returns:
        Список словників з ідентифікатором, ім’ям, фото та професією.
    """
    people = []
    seen = set()

    for person in crew:
        job = person.get("job", "") or ""
        person_id = person.get("id")

        if person_id in seen:
            continue

        matches = (
            job in jobs
            or (department and person.get("department") == department
                and any(k in job.lower() for k in keywords))
        )

        if not matches:
            continue

        seen.add(person_id)
        people.append({
            "tmdbId": person_id,
            "name": person.get("name", ""),
            "photo": image_url(person.get("profile_path"), "w500"),
            "job": job,
        })

    return people


def get_tmdb_data(title, year):
    """Отримує дутальну інформацію про фільм і знімальну групу з TMDb
    Args:
        title: Назва фільму
        year: Рік випуску
    Returns:
        Словник даних або порожній словник якщо збіг відсутній
        чи помилки HTTP-запиту деталей
    Raises:
        RuntimeError: Якщо токен TMDb не налаштовано.
    """
    if not TMDB_TOKEN:
        raise RuntimeError("Не знайдено TMDB_TOKEN у файлі .env")

    if is_wikidata_id(title):
        print(f"Немає назви, пропускаю пошук у TMDb: {title}")
        return {}

    match = find_tmdb_movie(title, year)

    if not match:
        print(f"Не знайдено в TMDb: {title} ({year})")
        return {}

    movie_id = match["id"]

    try:
        data = tmdb_request(
            f"movie/{movie_id}",
            {
                "language": "uk-UA",
                "append_to_response": "credits",
            },
        )

        if not data.get("overview"):
            try:
                english_data = tmdb_request(
                    f"movie/{movie_id}",
                    {"language": "en-US"},
                )
                data["overview"] = english_data.get("overview", "")
            except requests.RequestException:
                pass

        credits = data.get("credits", {})
        crew = credits.get("crew", [])

        cast = [
            {
                "tmdbId": person.get("id"),
                "name": person.get("name", ""),
                "character": person.get("character", ""),
                "photo": image_url(person.get("profile_path"), "w500"),
                "order": person.get("order"),
            }
            for person in credits.get("cast", [])
        ]

        return {
            "tmdbId": data.get("id"),
            "title": data.get("title", ""),
            "originalTitle": data.get("original_title", ""),
            "releaseDate": data.get("release_date", ""),
            "durationMin": data.get("runtime"),
            "description": data.get("overview", ""),

            "posterFile": image_url(data.get("poster_path"), "w500"),
            "backdropFile": image_url(data.get("backdrop_path"), "w1280"),

            "genres": [g.get("name", "") for g in data.get("genres", [])],
            "countries": [
                c.get("name", "") for c in data.get("production_countries", [])
            ],
            "languages": [
                l.get("english_name", "") for l in data.get("spoken_languages", [])
            ],
            "companies": [
                c.get("name", "") for c in data.get("production_companies", [])
            ],

            "rating": data.get("vote_average"),
            "voteCount": data.get("vote_count"),
            "popularity": data.get("popularity"),

            "cast": cast,
            "directors": people_by_jobs(crew, ("Director",)),
            "screenWriters": people_by_jobs(crew, ("Writer", "Screenplay", "Story")),
            "photographyDirectors": people_by_jobs(crew, ("Director of Photography",)),
            # "editors": people_by_jobs(crew, ("Editor",)),
            "editors": people_by_jobs(crew, jobs=("Editor", "Film Editor"), department="Editing", keywords=("editor",)),
            "composers": people_by_jobs(
                crew, ("Original Music Composer", "Composer", "Music")
            ),

            "tmdbUrl": f"https://www.themoviedb.org/movie/{movie_id}",
        }

    except requests.RequestException as e:
        print(f"Помилка деталей TMDb для «{title}»: {e}")
        return {}

def empty_record(film, title, year):
    """Створює початковий запис фільму з даними Wikidata та порожніми полями для доповнення"""
    return {
        "film": film["film"],
        "filmLabel": title,
        "year": year,

        "tmdbId": None,
        "title": "",
        "originalTitle": "",
        "releaseDate": "",
        "durationMin": None,
        "description": "",
        "posterFile": "",
        "backdropFile": "",
        "genres": [],
        "countries": [],
        "languages": [],
        "companies": [],
        "rating": None,
        "voteCount": None,
        "popularity": None,
        "cast": [],
        "directors": [],
        "screenWriters": [],
        "photographyDirectors": [],
        "editors": [],
        "composers": [],
        "tmdbUrl": "",
    }


def main():
    """Збирає та доповнює дані про фільми, записуючи кожен JSON-об’єкт в окремий рядок файлу"""
    if not TMDB_TOKEN:
        raise RuntimeError("TMDB_TOKEN відсутній")

    films = get_wikidata_films()
    print(f"Отримано фільмів із Wikidata: {len(films)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for index, film in enumerate(films, start=1):
            title = film["filmLabel"]
            year = film["year"]

            print(f"[{index}/{len(films)}] {title} ({year or 'рік невідомий'})")

            record = empty_record(film, title, year)

            tmdb_data = get_tmdb_data(title, year)
            if tmdb_data:
                record.update(tmdb_data)

            if not record["durationMin"]:
                record["durationMin"] = parse_duration(film.get("wikidataDuration"))

            file.write(json.dumps(record, ensure_ascii=False) + "\n")
            file.flush()
            time.sleep(0.3)

    print(f"\nДані збережено у {OUTPUT_FILE}")


def read_data(filename="movies.json"):
    """Зчитує фільми з файлу, де кожен рядок містить окремий JSON-об’єкт
    Args:
        filename: Шлях до файлу з даними
    Returns:
        Список записів; порожні та некоректні рядки пропускаються
    """
    movies = []
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                movies.append(json.loads(line))
            except json.JSONDecodeError as error:
                print(f"Помилка JSON у рядку {line_number}: {error}")
    return movies


if __name__ == "__main__":
    main()
