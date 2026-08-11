import logging
from functools import lru_cache

from app.clients.tmdb_client import tmdb_client
from app.data_processing.demographic_filtering import get_top_movies
from app.data_processing.content_based_filtering import (
    prepare_content_based_data,
    get_recommendations as get_content_recommendations,
)
from app.models.movie import Movie

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _content_based_dataset():
    return prepare_content_based_data()


def recommend_by_criteria(genre=None, n=10, min_rating=0):
    top_movies = get_top_movies(n * 2)
    logger.info("Retrieved %d top movies", len(top_movies))

    if top_movies.empty:
        logger.warning("No top movies retrieved")
        return []

    recommendations = [
        Movie(
            id=row['id'],
            title=row['title'],
            genres=row.get('genres', ''),
            rating=row.get('vote_average', 0),
        )
        for _, row in top_movies.iterrows()
    ]

    if genre:
        recommendations = [m for m in recommendations if genre.lower() in (m.genres or '').lower()]

    if min_rating:
        recommendations = [m for m in recommendations if m.rating >= min_rating]

    recommendations.sort(key=lambda m: m.rating, reverse=True)
    final_recommendations = recommendations[:n]

    if not final_recommendations:
        logger.warning("No recommendations after filtering, falling back to top rated")
        final_recommendations = [
            Movie(id=row['id'], title=row['title'], genres=row.get('genres', ''), rating=row.get('vote_average', 0))
            for _, row in top_movies.head(n).iterrows()
        ]

    return final_recommendations


def get_content_based_recommendations(title, n=10):
    df, cosine_sim, indices = _content_based_dataset()
    content_recommendations = get_content_recommendations(title, df, cosine_sim, indices)

    if content_recommendations.empty:
        logger.warning("No content-based recommendations found for '%s'", title)
        return []

    return [
        Movie(
            id=df.loc[idx, 'id'],
            title=df.loc[idx, 'title'],
            genres=df.loc[idx, 'genres'],
            rating=df.loc[idx, 'vote_average'],
        )
        for idx in content_recommendations.index[:n]
        if idx in df.index
    ]


def _enrich_with_tmdb(movie_id):
    return tmdb_client.get_movie(movie_id)


def recommend_by_title(title, n=10, genre=None, min_rating=0):
    search_results = tmdb_client.search_movies(title)
    if not search_results:
        return []

    movie_id = search_results[0]['id']
    tmdb_recommendations = tmdb_client.get_movie_recommendations(movie_id, n)

    results = []
    for movie in tmdb_recommendations:
        movie_data = _enrich_with_tmdb(movie['id'])
        if not movie_data:
            continue
        movie_genres = [g['name'] for g in movie_data.get('genres', [])]
        if (not genre or genre in movie_genres) and movie['vote_average'] >= min_rating:
            results.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_path': movie['poster_path'],
                'rating': movie['vote_average'],
                'genres': movie_genres,
                'overview': movie_data.get('overview', 'No overview available.'),
            })
    return results


def recommend_by_filters(genre, n, min_rating):
    local_recommendations = recommend_by_criteria(genre, n, min_rating)
    results = []
    for movie in local_recommendations:
        movie_data = _enrich_with_tmdb(movie.id)
        results.append({
            'id': movie.id,
            'title': movie.title,
            'rating': movie.rating,
            'genres': movie.genres,
            'poster_path': movie_data['poster_path'] if movie_data else None,
            'overview': movie_data.get('overview', 'No overview available.') if movie_data else 'No overview available.',
        })
    return results