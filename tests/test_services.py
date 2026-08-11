from unittest.mock import patch
import pandas as pd

from app.services import recommendation_service as service


def fake_top_movies(n=10):
    return pd.DataFrame([
        {"id": 1, "title": "The Shawshank Redemption", "genres": "Drama", "vote_average": 9.3},
        {"id": 2, "title": "The Dark Knight", "genres": "Action,Crime,Drama", "vote_average": 9.0},
        {"id": 3, "title": "Inception", "genres": "Action,Sci-Fi", "vote_average": 8.8},
        {"id": 4, "title": "The Notebook", "genres": "Romance,Drama", "vote_average": 7.8},
        {"id": 5, "title": "Superbad", "genres": "Comedy", "vote_average": 7.6},
    ])


@patch('app.services.recommendation_service.get_top_movies')
def test_recommend_by_criteria_filters_by_genre(mock_top):
    mock_top.side_effect = fake_top_movies
    results = service.recommend_by_criteria(genre="Drama", n=10)
    titles = {m.title for m in results}
    assert "The Shawshank Redemption" in titles
    assert "Superbad" not in titles


@patch('app.services.recommendation_service.get_top_movies')
def test_recommend_by_criteria_filters_by_min_rating(mock_top):
    mock_top.side_effect = fake_top_movies
    results = service.recommend_by_criteria(min_rating=9.0)
    assert all(m.rating >= 9.0 for m in results)
    assert len(results) == 2


@patch('app.services.recommendation_service.get_top_movies')
def test_recommend_by_criteria_empty_dataset_returns_empty(mock_top):
    mock_top.return_value = pd.DataFrame(columns=["id", "title", "genres", "vote_average"])
    results = service.recommend_by_criteria(genre="Drama")
    assert results == []


@patch('app.services.recommendation_service.tmdb_client')
def test_recommend_by_title_no_search_results_returns_empty(mock_client):
    mock_client.search_movies.return_value = []
    results = service.recommend_by_title("NoSuchMovieXYZ")
    assert results == []


@patch('app.services.recommendation_service.tmdb_client')
def test_recommend_by_title_with_results(mock_client):
    mock_client.search_movies.return_value = [{"id": 27205}]
    mock_client.get_movie_recommendations.return_value = [
        {"id": 100, "title": "Related Movie", "poster_path": "/x.jpg", "vote_average": 8.0},
    ]
    mock_client.get_movie.return_value = {
        "genres": [{"name": "Action"}], "overview": "Some overview",
    }
    results = service.recommend_by_title("Inception", n=5, genre="Action", min_rating=5)
    assert len(results) == 1
    assert results[0]["title"] == "Related Movie"

@patch('app.services.recommendation_service._content_based_dataset')
@patch('app.services.recommendation_service.get_content_recommendations')
def test_content_based_recommendations_returns_movies(mock_get_content, mock_dataset):
    df = pd.DataFrame({
        'id': [10, 20],
        'title': ['Movie A', 'Movie B'],
        'genres': ['Action', 'Drama'],
        'vote_average': [7.5, 6.0],
    })
    mock_dataset.return_value = (df, None, None)
    mock_get_content.return_value = pd.Series(['Movie B'], index=[1])

    results = service.get_content_based_recommendations('Movie A', n=5)
    assert len(results) == 1
    assert results[0].title == 'Movie B'

@patch('app.services.recommendation_service._content_based_dataset')
@patch('app.services.recommendation_service.get_content_recommendations')
def test_content_based_recommendations_empty(mock_get_content, mock_dataset):
    df = pd.DataFrame(columns=['id', 'title', 'genres', 'vote_average'])
    mock_dataset.return_value = (df, None, None)
    mock_get_content.return_value = pd.Series(dtype=object)

    results = service.get_content_based_recommendations('Unknown Movie')
    assert results == []


@patch('app.services.recommendation_service.tmdb_client')
@patch('app.services.recommendation_service.get_top_movies')
def test_recommend_by_filters_enriches_with_tmdb(mock_top, mock_client):
    mock_top.side_effect = fake_top_movies
    mock_client.get_movie.return_value = {'poster_path': '/p.jpg', 'overview': 'desc'}

    results = service.recommend_by_filters(genre="Drama", n=10, min_rating=0)
    assert len(results) > 0
    assert results[0]['poster_path'] == '/p.jpg'