import re
from urllib.parse import unquote

from rdflib import Graph, URIRef, Literal

graph = Graph()
graph.parse("movies_graph.ttl", format='turtle')

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

# def get_movie_info(movie_id):
#     request = """
#         PREFIX ex: <http://ukrainian-movies.org/>
#         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#
#         SELECT ?title ?releaseDate ?year ?country ?genre ?language ?director ?screenWriter ?photographyDirector
#                ?editor ?composer ?company ?distributor ?durationMin ?posterFile ?cast
#
#         WHERE {
#             ?movie a ex:Movie ;
#                    rdfs:label ?title .
#
#             OPTIONAL { ?movie ex:ReleaseDate ?releaseDate . }
#             OPTIONAL { ?movie ex:Year ?year . }
#             OPTIONAL { ?movie ex:Country ?countryNode . ?countryNode rdfs:label ?country . }
#             OPTIONAL { ?movie ex:Genre ?genreNode . ?genreNode rdfs:label ?genre . }
#             OPTIONAL { ?movie ex:Language ?languageNode . ?languageNode rdfs:label ?language . }
#             OPTIONAL { ?movie ex:Director ?directorNode . ?directorNode rdfs:label ?director . }
#             OPTIONAL { ?movie ex:ScreenWriter ?screenWriter . }
#             OPTIONAL { ?movie ex:PhotographyDirector ?photographyDirector . }
#             OPTIONAL { ?movie ex:Editor ?editor . }
#             OPTIONAL { ?movie ex:Composer ?composer . }
#             OPTIONAL { ?movie ex:Company ?companyNode . ?companyNode rdfs:label ?company . }
#             OPTIONAL { ?movie ex:Distributor ?distributor . }
#             OPTIONAL { ?movie ex:Duration ?durationMin . }
#             OPTIONAL { ?movie ex:Poster ?posterFile . }
#             OPTIONAL { ?movie ex:Cast ?castNode . ?castNode rdfs:label ?cast . }
#         }
#     """
#     movie_uri = URIRef(f"http://ukrainian-movies.org/movie/{movie_id}")
#
#     result = graph.query(
#         request,
#         initBindings={"movie": movie_uri}
#     )
#     # result = graph.query(request, initBindings={"movie_id": URIRef(movie_id)})
#     movie = None
#
#     for row in result:
#         if movie is None:
#             movie = {
#                 "id": movie_id,
#                 "title": str(row.title),
#                 "releaseDate": str(row.releaseDate)[:4],
#                 "country": str(row.country),
#                 "genres": [],
#                 "language": str(row.language),
#                 "director": str(row.director),
#                 "screenWriter": str(row.screenWriter),
#                 "photographyDirector": str(row.photographyDirector),
#                 "editor": str(row.editor),
#                 "composer": str(row.composer),
#                 "company": str(row.company),
#                 "distributor": str(row.distributor),
#                 "cast": [],
#                 "durationMin": str(row.durationMin),
#                 "posterFile": str(row.posterFile),
#                 "description": str(row.description)
#             }
#         for key, value in [
#             ("genres", row.genres),
#             ("cast", row.cast)
#         ]:
#             if value:
#                 label = str(value).rsplit('/', 1)[-1].replace("_", " ")
#                 if label not in movie[key]:
#                     movie[key].append(label)
#
#     return movie

def val(x):
    return str(x) if x is not None else None

def label_of(x):
    return str(x).rsplit('/', 1)[-1].replace("_", " ")

def get_movie_cast(movie_id):
    query = """
        PREFIX ex: <http://ukrainian-movies.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?person ?name ?photo ?character ?order
        WHERE {
            ?movie ex:CastEntry ?entry .
            ?entry ex:Person ?person .
            ?person rdfs:label ?name .
            OPTIONAL { ?entry ex:CastOrder ?order . }
            OPTIONAL { ?entry ex:Character ?character . }
            OPTIONAL { ?person ex:Photo ?photo . }
        }
        ORDER BY ?order
    """
    movie_uri = URIRef(f"http://ukrainian-movies.org/movie/{movie_id}")
    result = graph.query(query, initBindings={"movie": movie_uri})

    cast = {}
    for r in result:
        pid = str(r.person).rsplit("/", 1)[-1]
        if pid not in cast:
            cast[pid] = {
                "id": pid,
                "name": str(r.name),
                "photo": str(r.photo) if r.photo else None,
                "characters": [],
            }
        if r.character and str(r.character) not in cast[pid]["characters"]:
            cast[pid]["characters"].append(str(r.character))

    return list(cast.values())

def ref(node, name):
    return {"id": str(node).rsplit("/", 1)[-1], "name": str(name)}

def get_movie_info(movie_id):
    request = """
        PREFIX ex: <http://ukrainian-movies.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?title ?releaseDate ?year ?country ?genre ?language ?directorNode ?director
               ?screenWriterNode ?screenWriter ?photographyDirectorNode ?photographyDirector
               ?editorNode ?editor ?composerNode ?composer ?companyNode ?company
               ?distributorNode ?distributor ?durationMin ?posterFile ?description
        WHERE {
            ?movie a ex:Movie ;
                   rdfs:label ?title .

            OPTIONAL { ?movie ex:ReleaseDate ?releaseDate . }
            OPTIONAL { ?movie ex:Year ?year . }
            OPTIONAL { ?movie ex:Country ?countryNode . ?countryNode rdfs:label ?country . }
            OPTIONAL { ?movie ex:Genre ?genreNode . ?genreNode rdfs:label ?genre . }
            OPTIONAL { ?movie ex:Language ?languageNode . ?languageNode rdfs:label ?language . }
            OPTIONAL { ?movie ex:Director ?directorNode . ?directorNode rdfs:label ?director . }
            OPTIONAL { ?movie ex:ScreenWriter ?screenWriterNode . ?screenWriterNode rdfs:label ?screenWriter . }
            OPTIONAL { ?movie ex:PhotographyDirector ?photographyDirector . }
            OPTIONAL { ?movie ex:Editor ?editor . }
            OPTIONAL { ?movie ex:Composer ?composer . }
            OPTIONAL { ?movie ex:Company ?companyNode . ?companyNode rdfs:label ?company . }
            OPTIONAL { ?movie ex:Distributor ?distributor . }
            OPTIONAL { ?movie ex:Duration ?durationMin . }
            OPTIONAL { ?movie ex:Poster ?posterFile . }
            OPTIONAL { ?movie ex:Description ?description . }
        }
    """
    movie_uri = URIRef(f"http://ukrainian-movies.org/movie/{movie_id}")
    result = graph.query(request, initBindings={"movie": movie_uri})

    movie = None
    for row in result:
        if movie is None:
            movie = {
                "id": movie_id,
                "title": val(row.title),
                "releaseDate": val(row.releaseDate)[:4] if row.releaseDate else None,
                "country": val(row.country),
                "language": val(row.language),
                "company": (
                    {"id": unquote(str(row.companyNode).rsplit("/", 1)[-1]),
                     "name": str(row.company)}
                    if row.company else None
                ),
                "durationMin": val(row.durationMin),
                "posterFile": val(row.posterFile),
                "description": val(row.description),
                "genres": [],
                "cast": [],
                **{key: [] for key, _, _ in PEOPLE_FIELDS},
            }
        if row.genre and str(row.genre) not in movie["genres"]:
            movie["genres"].append(str(row.genre))
        for key, node_var, name_var in PEOPLE_FIELDS:
            node, name = row.get(node_var), row.get(name_var)
            if node is not None and name is not None:
                person = ref(node, name)
                if person not in movie[key]:
                    movie[key].append(person)

    if movie is not None:
        movie["cast"] = get_movie_cast(movie_id)
    return movie

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

def filter_data(filter_queue):
    pass