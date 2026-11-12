"""Побудова RDF-графа українських фільмів та збереження у форматі Turtle"""
from urllib.parse import quote
import rdflib
from rdflib import RDF, RDFS, Literal, XSD, URIRef
from rdflib.namespace import Namespace
from load_data import read_data

EX = Namespace("http://ukrainian-movies.org/")
g = rdflib.Graph()
g.bind("ex", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

def make_uri(value):
    """Створює RDF-посилання URIRef із переданого значення"""
    return URIRef(str(value))

def add_literal(subject, predicate, value, datatype=None):
    """Додає літеральне значення до графа, пропускаючи None і порожні рядки
    Args:
        subject: RDF-суб’єкт
        predicate: RDF-предикат
        value: Значення, яке необхідно додати
        datatype: Необов’язковий RDF-тип даних
    """
    if value is None or value == "":
        return
    g.add((subject, predicate, Literal(value, datatype=datatype) if datatype else Literal(value)))

def add_named_entities(movie_uri, relation, entity_type, values):
    """Створює іменовані RDF-сутності та пов’язує їх із фільмом
    Args:
        movie_uri: URI фільму
        relation: Предикат зв’язку
        entity_type: RDF-клас створюваних сутностей
        values: Список назв сутностей
    """
    for value in values or []:
        if not isinstance(value, str) or not value.strip():
            continue

        value = value.strip()
        entity_uri = EX[
            f"{entity_type.split('/')[-1]}/{quote(value, safe='')}"
        ]

        g.add((entity_uri, RDF.type, entity_type))
        g.add((entity_uri, RDFS.label, Literal(value)))
        g.add((movie_uri, relation, entity_uri))

def add_person(movie_uri, relation, person, role=None):
    """Створює RDF-вузол людини та пов’язує його з фільмом заданим предикатом
    Використовує ідентифікатор TMDb або ім’я для формування URI
    Args:
        movie_uri: URI фільму
        relation: Предикат зв’язку між фільмом і людиною
        person: Ім’я або словник із даними людини
        role: Роль у знімальній групі
    Returns:
        URI людини або None, якщо дані некоректні чи ім’я відсутнє
    """
    if isinstance(person, str):
        person = {"name": person}

    if not isinstance(person, dict):
        return

    name = person.get("name", "").strip()
    if not name:
        return

    tmdb_id = person.get("tmdbId")

    if tmdb_id:
        person_uri = EX[f"person/tmdb/{tmdb_id}"]
    else:
        person_uri = EX[f"person/{quote(name, safe='')}"]

    g.add((person_uri, RDF.type, EX.Person))
    g.add((person_uri, RDFS.label, Literal(name)))
    g.add((movie_uri, relation, person_uri))

    if tmdb_id is not None:
        add_literal(person_uri, EX.TMDBId, tmdb_id, XSD.integer)

    photo = person.get("photo")
    if photo:
        g.add((person_uri, EX.Photo, URIRef(photo)))

    # if person.get("character"):
    #     add_literal(person_uri, EX.Character, person["character"])
    #
    # if person.get("order") is not None:
    #     add_literal(person_uri, EX.CastOrder, person["order"], XSD.integer)

    if role:
        add_literal(person_uri, EX.CrewRole, role)

    if person.get("job"):
        add_literal(person_uri, EX.CrewRole, person["job"])

    return person_uri

def add_cast_entry(movie_uri, film_id, person):
    """Створює запис акторського складу зі зв’язками з фільмом та актором
    Args:
        movie_uri: URI фільму
        film_id: Ідентифікатор фільму
        person: Ім’я або словник із даними актора, роллю та порядком у титрах
    """
    if isinstance(person, str):
        person = {"name": person}
    person_uri = add_person(movie_uri, EX.Cast, person)
    if person_uri is None:
        return
    key = person.get("tmdbId") or quote(person["name"].strip(), safe="")
    entry_uri = EX[f"cast/{film_id}_{key}"]
    g.add((entry_uri, RDF.type, EX.CastEntry))
    g.add((movie_uri, EX.CastEntry, entry_uri))
    g.add((entry_uri, EX.Person, person_uri))
    add_literal(entry_uri, EX.Character, person.get("character"))
    add_literal(entry_uri, EX.CastOrder, person.get("order"), XSD.integer)


def create_graph():
    """Формує RDF-граф із записів фільмів та зберігає його у файлі Turtle"""
    global g
    g = rdflib.Graph()
    g.bind("ex", EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    movies = read_data("movies.json")

    for movie in movies:
        wikidata_uri = movie.get("film", "")
        film_id = wikidata_uri.rstrip("/").split("/")[-1]

        if not film_id:
            print("Пропущено запис без ID Wikidata")
            continue

        movie_uri = EX[f"movie/{film_id}"]

        g.add((movie_uri, RDF.type, EX.Movie))
        title = movie.get("title") or movie.get("filmLabel")
        add_literal(movie_uri, RDFS.label, title)
        add_literal(movie_uri, EX.WikidataURI, URIRef(wikidata_uri) if wikidata_uri else None)
        add_literal(movie_uri, EX.WikidataId, film_id)
        add_literal(movie_uri, EX.TMDBId, movie.get("tmdbId"), XSD.integer)
        add_literal(movie_uri, EX.OriginalTitle, movie.get("originalTitle"))
        add_literal(movie_uri, EX.Year, movie.get("year"), XSD.gYear)
        release_date = movie.get("releaseDate")
        if release_date:
            add_literal(movie_uri, EX.ReleaseDate, release_date, XSD.date)
        add_literal(movie_uri, EX.Duration, movie.get("durationMin"), XSD.integer)
        add_literal(movie_uri, EX.Description, movie.get("description"))

        poster = movie.get("posterFile")
        if poster:
            g.add((movie_uri, EX.Poster, URIRef(poster)))

        backdrop = movie.get("backdropFile")
        if backdrop:
            g.add((movie_uri, EX.Backdrop, URIRef(backdrop)))

        add_literal(movie_uri, EX.Rating, movie.get("rating"), XSD.float)
        add_literal(movie_uri, EX.VoteCount, movie.get("voteCount"), XSD.integer)
        add_literal(movie_uri, EX.Popularity, movie.get("popularity"), XSD.float)
        add_literal(movie_uri, EX.TMDBUrl, URIRef(movie["tmdbUrl"]) if movie.get("tmdbUrl") else None)
        add_named_entities(movie_uri, EX.Genre, EX.Genre, movie.get("genres", []))
        add_named_entities(movie_uri, EX.Country, EX.Country, movie.get("countries", []))
        add_named_entities(movie_uri, EX.Language, EX.Language, movie.get("languages", []))
        add_named_entities(movie_uri, EX.Company, EX.Company, movie.get("companies", []))

        for person in movie.get("directors", []):
            add_person(movie_uri, EX.director, person)

        for person in movie.get("cast", []):
            add_cast_entry(movie_uri, film_id, person)

        for person in movie.get("screenWriters", []):
            add_person(movie_uri, EX.screenWriter, person)

        for person in movie.get("cast", []):
            add_person(movie_uri, EX.Cast, person)

        for person in movie.get("photographyDirectors", []):
            add_person(movie_uri, EX.cinematographer, person)

        for person in movie.get("editors", []):
            add_person(movie_uri, EX.editor, person)

        for person in movie.get("composers", []):
            add_person(movie_uri, EX.composer, person)

    output_file = "movies_graph.ttl"
    g.serialize(destination=output_file, format="turtle")

    print(f"Граф збережено: {output_file}")
    print(f"Кількість RDF-трійок: {len(g)}")


if __name__ == "__main__":
    create_graph()
