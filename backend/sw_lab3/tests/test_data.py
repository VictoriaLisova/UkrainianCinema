"""Тести отримання та обробки даних RDF-графа, пошуку, фільтрації і кешування"""
import pytest
from rdflib import RDFS, Literal
from server_data_preparation import get_all_movies

def test_one_existing_value(data):
    """Перевіряє отримання наявного значення RDF у вигляді рядка"""
    assert data.one(data.EX["movie/Q1"], RDFS.label) == "Довбуш"

def test_one_missing_value(data):
    """Перевіряє повернення None за відсутності значення у графі"""
    assert data.one(data.EX["movie/Q3"], data.EX.Year) is None

def test_labeled_entities(data):
    """Перевіряє отримання назв пов’язаних RDF-сутностей"""
    genres = data.labeled(data.EX["movie/Q1"], data.EX.Genre)
    assert {item["name"] for item in genres} == {"Драма", "Історичний"}

def test_catalog_unique_movies(data):
    """Перевіряє відсутність дублікатів, збереження жанрів і першість повного запису в каталозі"""
    movies = data.get_all_movies()
    assert len(movies) == 3
    assert {movie["id"] for movie in movies} == {"Q1", "Q2", "Q3"}
    assert movies[0]["id"] == "Q1"
    assert set(movies[0]["genres"]) == {"Драма", "Історичний"}

def test_movie_details(data):
    """Перевіряє назву, рік випуску та режисера відомого фільму"""
    movie = data.get_movie_info("Q1")
    assert movie["title"] == "Довбуш"
    assert movie["year"] == "2023"
    assert movie["directors"] == [{"id": "10", "name": "Тестовий режисер"}]

def test_unknown_movie(data):
    """Перевіряє повернення None для відсутнього у графі фільму"""
    assert data.get_movie_info("UNKNOWN") is None

def test_movie_without_optional_fields(data):
    """Перевіряє обробку відсутніх необов’язкових характеристик фільму"""
    movie = data.get_movie_info("Q3")
    assert movie["year"] is None
    assert movie["posterFile"] is None
    assert movie["cast"] == []

def test_cast_order_and_grouping(data):
    """Перевіряє порядок акторів та об’єднання ролей одного актора"""
    cast = data.get_movie_cast("Q1")
    assert [person["id"] for person in cast] == ["30", "20"]
    assert set(cast[1]["characters"]) == {"Герой", "Оповідач"}


def test_actor_filmography(data):
    """Перевіряє отримання фільмографії актора"""
    result = data.search_by_member("20")
    assert result["person"] == {"id": "20", "name": "Перший актор"}
    assert [movie["id"] for movie in result["movies"]] == ["Q1"]


def test_unknown_person(data):
    """Перевіряє результат пошуку людини, відсутньої у графі"""
    assert data.search_by_member("UNKNOWN") == {
        "person": None, "movies": []
    }

@pytest.mark.parametrize("query", ["довбуш", "ДОВБУШ", "  Довбуш  "])
def test_search_by_title(data, query):
    """Перевіряє пошук за назвою незалежно від регістру літер і крайніх пробілів"""
    assert data.get_suggestions(query) == [
        {"id": "Q1", "title": "Довбуш", "year": "2023"}
    ]

@pytest.mark.parametrize("query", ["", "Д", "невідомий фільм"])
def test_search_without_results(data, query):
    """Перевіряє пошук за порожнім, коротким і невідомим текстом"""
    assert data.get_suggestions(query) == []

def test_filter_by_genre(data):
    """Перевіряє, що фільтрація повертає лише фільми заданого жанру"""
    movies = data.filter_data(genre="Драма")
    assert {movie["id"] for movie in movies} == {"Q1", "Q2"}

def test_filter_by_year(data):
    """Перевіряє фільтрацію фільмів за заданим діапазоном років"""
    movies = data.filter_data(from_year="2023", to_year="2023")
    assert [movie["id"] for movie in movies] == ["Q1"]

def test_combined_filters(data):
    """Перевіряє одночасне застосування фільтрів за жанром і роками"""
    movies = data.filter_data(
        genre="Драма", from_year="2017", to_year="2020"
    )
    assert [movie["id"] for movie in movies] == ["Q2"]

def test_filter_without_results(data):
    """Перевіряє повернення порожнього списку для невідомого жанру"""
    assert data.filter_data(genre="Невідомий жанр") == []

@pytest.mark.parametrize("order, expected", [
    ("asc", ["Q2", "Q1", "Q3"]),
    ("desc", ["Q1", "Q2", "Q3"]),
])
def test_sort_by_year(data, order, expected):
    """Перевіряє сортування за роком у двох напрямках і розміщення записів без року"""
    assert [movie["id"] for movie in data.filter_data(
        order=order
    )] == expected

def test_genres_unique_and_sorted(data):
    """Перевіряє унікальність та впорядкованість списку жанрів"""
    assert data.get_genres() == sorted([
        "Драма", "Історичний", "Анімація"
    ])

def test_cache_calls_catalog_once(data, monkeypatch):
    """Перевіряє, що повторне звернення до кешу не завантажує каталог знову"""
    calls = []

    def fake_get_all_movies():
        """Імітує завантаження каталогу та фіксує кількість викликів"""
        calls.append(1)
        return [{"id": "Q1"}]

    monkeypatch.setattr(data, "get_all_movies", fake_get_all_movies)
    assert data.all_movies_cached() == [{"id": "Q1"}]
    assert data.all_movies_cached() == [{"id": "Q1"}]
    assert len(calls) == 1

def test_director_filmography(data):
    """Перевіряє, що пошук за режисером повертає пов’язаний з ним фільм"""
    result = data.search_by_member("10")
    assert result["person"] == {
        "id": "10", "name": "Тестовий режисер"
    }
    assert [movie["id"] for movie in result["movies"]] == ["Q1"]

@pytest.mark.parametrize("predicate", [
    "screenWriter",
    "cinematographer",
    "editor",
    "composer"
])
def test_crew_filmography(data, predicate):
    """Перевіряє пошук фільмів за різними професіями учасників знімальної групи"""
    person = data.EX["person/tmdb/40"]

    data.graph.add((
        person,
        RDFS.label,
        Literal("Тестовий учасник")
    ))

    data.graph.add((
        data.EX["movie/Q1"],
        data.EX[predicate],
        person
    ))

    result = data.search_by_member("40")

    assert result["person"] == {
        "id": "40",
        "name": "Тестовий учасник"
    }

    assert [movie["id"] for movie in result["movies"]] == ["Q1"]