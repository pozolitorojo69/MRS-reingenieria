from flask import Blueprint, jsonify, request

from app.clients.tmdb_client import tmdb_client
from app.services import recommendation_service as service

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/recommendations')
def get_movie_recommendations():
    genre = request.args.get('genre', '')
    n = request.args.get('n', default=10, type=int)
    min_rating = request.args.get('min_rating', default=0, type=float)
    title = request.args.get('title', '')

    if title:
        recommendations = service.recommend_by_title(title, n, genre, min_rating)
    else:
        recommendations = service.recommend_by_filters(genre, n, min_rating)

    return jsonify(recommendations)


@bp.route('/movie/<int:movie_id>')
def get_movie_details(movie_id):
    movie_data = tmdb_client.get_movie(movie_id)
    if movie_data:
        return jsonify(movie_data)
    return jsonify({'error': 'Movie not found'}), 404


@bp.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500