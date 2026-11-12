"""Підготовка ізольованих RDF-даних для модульного тестування"""
import sys
from pathlib import Path
import pytest
from rdflib import Graph

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

@pytest.fixture
def data(monkeypatch):
    """Створює окремий RDF-граф із трьома умовними фільмами
    Тимчасово замінює граф і кеш застосунку для ізоляції тестів.
    Args:
        monkeypatch: Фікстура pytest для тимчасової заміни атрибутів
    Returns:
        Модуль роботи з даними, налаштований на тестовий граф
    """
    monkeypatch.chdir(BACKEND_DIR)
    import server_data_preparation as data_module

    graph = Graph().parse(data="""
        @prefix ex: <http://ukrainian-movies.org/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        <http://ukrainian-movies.org/movie/Q1> a ex:Movie ;
            rdfs:label "Довбуш" ;
            ex:Year "2023" ;
            ex:Poster <https://example.org/poster.jpg> ;
            ex:Genre ex:drama, ex:history ;
            ex:director <http://ukrainian-movies.org/person/tmdb/10> ;
            ex:CastEntry ex:cast1, ex:cast2, ex:cast3 .

        <http://ukrainian-movies.org/movie/Q2> a ex:Movie ;
            rdfs:label "Кіборги" ;
            ex:Year "2017" ;
            ex:Genre ex:drama .

        <http://ukrainian-movies.org/movie/Q3> a ex:Movie ;
            rdfs:label "Мавка" ;
            ex:Genre ex:animation .

        ex:drama rdfs:label "Драма" .
        ex:history rdfs:label "Історичний" .
        ex:animation rdfs:label "Анімація" .

        <http://ukrainian-movies.org/person/tmdb/10>
            rdfs:label "Тестовий режисер" .
        <http://ukrainian-movies.org/person/tmdb/20>
            rdfs:label "Перший актор" .
        <http://ukrainian-movies.org/person/tmdb/30>
            rdfs:label "Другий актор" .

        ex:cast1 ex:Person <http://ukrainian-movies.org/person/tmdb/20> ;
            ex:CastOrder 1 ; ex:Character "Герой" .
        ex:cast2 ex:Person <http://ukrainian-movies.org/person/tmdb/30> ;
            ex:CastOrder 0 ; ex:Character "Друг" .
        ex:cast3 ex:Person <http://ukrainian-movies.org/person/tmdb/20> ;
            ex:CastOrder 1 ; ex:Character "Оповідач" .
    """, format="turtle")

    monkeypatch.setattr(data_module, "graph", graph)
    monkeypatch.setattr(data_module, "_movies_cache", None)
    return data_module
