from urllib.parse import unquote
from rdflib import Graph, URIRef, Literal, RDFS, Namespace

EX = Namespace("http://ukrainian-movies.org/")

graph = Graph()
graph.parse("movies_graph.ttl", format='turtle')
_movies_cache = None

PEOPLE_FIELDS = [
    ("director", "directorNode", "director"),
    ("screenWriter", "screenWriterNode", "screenWriter"),
    ("photographyDirector", "photographyDirectorNode", "photographyDirector"),
    ("editor", "editorNode", "editor"),
    ("composer", "composerNode", "composer"),
]

def get_all_movies():
    request = """
        PREFIX ex: <http://ukrainian-movies.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?movie ?title ?year ?releaseDate ?genre ?poster
        WHERE {
            ?movie a ex:Movie ;
                   rdfs:label ?title .

            OPTIONAL {?movie ex:Year ?year .}
            OPTIONAL {?movie ex:ReleaseDate ?releaseDate .}
            OPTIONAL {
                ?movie ex:Genre ?genreNode .
                ?genreNode rdfs:label ?genre .
            }
            OPTIONAL {?movie ex:Poster ?poster .}
        }
    """

    results = graph.query(request)
    movies = {}
    for row in results:
        movie_uri = str(row.movie)
        movie_id = movie_uri.rsplit("/", 1)[-1]
        if movie_id not in movies:
            movies[movie_id] = {
                "id": movie_id,
                "title": str(row.title),
                "poster": str(row.poster) if row.poster else None,
                "date": str(row.year) if row.year else None,
                "genres": []
            }
        if row.genre:
            genre = str(row.genre)
            if genre not in movies[movie_id]["genres"]:
                movies[movie_id]["genres"].append(genre)

    data = list(movies.values())

    data.sort(
        key=lambda x: all([
            x["title"],
            x["poster"],
            x["date"],
            x["genres"]
        ]),
        reverse=True
    )
    for item in data:
        print(item)

    return data

def one(subject, predicate):
    value = graph.value(subject, predicate)
    return str(value) if value is not None else None


def labeled(subject, predicate):
    items = []
    for node in graph.objects(subject, predicate):
        name = graph.value(node, RDFS.label)
        if name is None:
            continue
        item = {
            "id": unquote(str(node).rsplit("/", 1)[-1]),
            "name": str(name),
        }
        if item not in items:
            items.append(item)
    return items


def get_movie_cast(movie_id):
    movie_uri = URIRef(f"http://ukrainian-movies.org/movie/{movie_id}")
    cast = {}

    for entry in graph.objects(movie_uri, EX.CastEntry):
        person = graph.value(entry, EX.Person)
        if person is None:
            continue

        name = graph.value(person, RDFS.label)
        if name is None:
            continue

        pid = str(person).rsplit("/", 1)[-1]
        order = graph.value(entry, EX.CastOrder)
        character = graph.value(entry, EX.Character)

        if pid not in cast:
            cast[pid] = {
                "id": pid,
                "name": str(name),
                "photo": one(person, EX.Photo),
                "order": int(order) if order is not None else 999,
                "characters": [],
            }
        if character is not None and str(character) not in cast[pid]["characters"]:
            cast[pid]["characters"].append(str(character))

    return sorted(cast.values(), key=lambda c: c["order"])


def get_movie_info(movie_id):
    m = URIRef(f"http://ukrainian-movies.org/movie/{movie_id}")
    if (m, RDFS.label, None) not in graph:
        return None

    release = one(m, EX.ReleaseDate)

    return {
        "id": movie_id,
        "title": one(m, RDFS.label),
        "originalTitle": one(m, EX.OriginalTitle),
        "releaseDate": release,
        "year": one(m, EX.Year),
        "durationMin": one(m, EX.Duration),
        "posterFile": one(m, EX.Poster),
        "backdropFile": one(m, EX.Backdrop),
        "description": one(m, EX.Description),
        "rating": one(m, EX.Rating),

        "genres": [x["name"] for x in labeled(m, EX.Genre)],
        "countries": [x["name"] for x in labeled(m, EX.Country)],
        "languages": [x["name"] for x in labeled(m, EX.Language)],
        "companies": labeled(m, EX.Company),

        "directors": labeled(m, EX.director),
        "screenWriters": labeled(m, EX.screenWriter),
        "photographyDirectors": labeled(m, EX.cinematographer),
        "editors": labeled(m, EX.editor),
        "composers": labeled(m, EX.composer),

        "cast": get_movie_cast(movie_id),
    }

def search_by_member(person_id):
    request = """
        PREFIX ex: <http://ukrainian-movies.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?movie ?title ?year ?poster ?person ?name ?role ?member ?genre
        WHERE {
            ?movie a ex:Movie ;
                    rdfs:label ?title .
            {
                ?movie ex:CastEntry ?cast .
                ?cast ex:Person ?person .
                OPTIONAL { ?cast ex:Character ?member . }
            }
            UNION { ?movie ex:Director ?person . }
            UNION { ?movie ex:ScreenWriter ?person . }
            UNION { ?movie ex:PhotographyDirector ?person . }
            UNION { ?movie ex:Editor ?person . }
            UNION { ?movie ex:Composer ?person . }
            ?person rdfs:label ?name .
            OPTIONAL { ?movie ex:Year ?year . }
            OPTIONAL { ?movie ex:Poster ?poster . }
            OPTIONAL { ?movie ex:Genre ?genreNode . ?genreNode rdfs:label ?genre . }
        }
    """
    person_uri = URIRef(f"http://ukrainian-movies.org/person/tmdb/{person_id}")
    result = graph.query(request, initBindings={"person": person_uri})
    person = None
    movies = {}
    for row in result:
        if person is None:
            person = {"id": person_id, "name": str(row.name)}
        movie_id = str(row.movie).rsplit("/", 1)[-1]
        if movie_id not in movies:
            movies[movie_id] = {
                "id": movie_id,
                "title": str(row.title),
                "poster": str(row.poster) if row.poster else None,
                "date": str(row.year) if row.year else None,
                "genres": []
            }
        movie = movies[movie_id]
        if row.genre and str(row.genre) not in movie["genres"]:
            movie["genres"].append(str(row.genre))

    return { "person": person, "movies": list(movies.values()) }

def get_suggestions(query_text):
    query_text = query_text.strip()

    if len(query_text) < 2:
        return []

    request = """
        PREFIX ex: <http://ukrainian-movies.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?movie ?title ?year
        WHERE {
            ?movie a ex:Movie ;
                   rdfs:label ?title .

            OPTIONAL { ?movie ex:Year ?year . }

            FILTER(
                CONTAINS(
                    LCASE(STR(?title)),
                    LCASE(STR(?search))
                )
            )
        }
    """

    results = graph.query(
        request,
        initBindings={"search": Literal(query_text)}
    )

    movies = {}

    for row in results:
        movie_id = str(row.movie).rstrip("/").rsplit("/", 1)[-1]

        movies[movie_id] = {
            "id": movie_id,
            "title": str(row.title),
            "year": str(row.year) if row.year else None
        }

    suggestions = sorted(
        movies.values(),
        key=lambda movie: (
            not movie["title"].casefold().startswith(query_text.casefold()),
            movie["title"].casefold()
        )
    )

    return suggestions[:5]

def all_movies_cached():
    global _movies_cache
    if _movies_cache is None:
        _movies_cache = get_all_movies()
    return _movies_cache

def filter_data(genre=None, order=None, from_year=None, to_year=None):
    movies = list(all_movies_cached())

    if genre:
        movies = [m for m in movies if genre in m["genres"]]

    if from_year or to_year:
        lo = int(from_year) if from_year else 0
        hi = int(to_year) if to_year else 9999
        movies = [m for m in movies if m["date"] and lo <= int(m["date"]) <= hi]

    if order in ("asc", "desc"):
        with_year = [m for m in movies if m["date"]]
        without_year = [m for m in movies if not m["date"]]
        with_year.sort(key=lambda m: int(m["date"]), reverse=(order == "desc"))
        movies = with_year + without_year

    return movies

def get_genres():
    return sorted({g for m in all_movies_cached() for g in m["genres"]})