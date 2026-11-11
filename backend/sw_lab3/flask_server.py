from flask import Flask, jsonify, request
from flask_cors import CORS
from server_data_preparation import (get_all_movies, get_movie_info, search_by_member, get_suggestions,
                                     filter_data, get_genres)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify(get_all_movies())

@app.route('/movie/<id>')
def movie_about(id):
    return jsonify(get_movie_info(id))

@app.route('/<person_id>/movies')
def search_by_member_id(person_id):
    return jsonify(search_by_member(person_id))

@app.route('/suggestions')
def suggestions():
    query_params = request.args.get("q", "").strip()
    return jsonify(get_suggestions(query_params))

@app.route('/genres')
def genres():
    return jsonify(get_genres())

@app.route('/filter')
def filtration():
    genre = request.args.get("genre", "").strip() or None
    order = request.args.get("order", "").strip() or None
    from_year = request.args.get("from_year", "").strip() or None
    to_year = request.args.get("to_year", "").strip() or None

    for value in (from_year, to_year):
        if value is not None and not value.isdigit():
            return jsonify({"error": "Рік має бути числом"}), 400

    return jsonify(filter_data(
        genre=genre,
        order=order,
        from_year=from_year,
        to_year=to_year,
    ))


if __name__ == '__main__':
    app.run(debug=True)