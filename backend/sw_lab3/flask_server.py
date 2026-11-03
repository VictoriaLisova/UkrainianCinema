from flask import Flask, jsonify, request
from flask_cors import CORS
from server_data_preparation import get_all_movies, get_movie_info, search_by_member, get_suggestions, filter_data

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

@app.route('/filter')
def filtration():
    query_params = request.args.get("q", "").strip()
    return jsonify(filter_data(query_params))

if __name__ == '__main__':
    app.run(debug=True)