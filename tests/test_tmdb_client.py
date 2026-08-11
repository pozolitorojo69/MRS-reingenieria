from unittest.mock import patch, MagicMock
import requests

from app.clients.tmdb_client import TMDBClient


def make_client():
    return TMDBClient(api_key="fake-key")


@patch('app.clients.tmdb_client.requests.get')
def test_get_movie_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {'id': 27205, 'title': 'Inception'}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = make_client().get_movie(27205)
    assert result['title'] == 'Inception'


@patch('app.clients.tmdb_client.requests.get')
def test_get_movie_returns_none_on_request_failure(mock_get):
    mock_get.side_effect = requests.RequestException("network error")
    result = make_client().get_movie(27205)
    assert result is None


@patch('app.clients.tmdb_client.requests.get')
def test_search_movies_returns_results_list(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {'results': [{'id': 1, 'title': 'A'}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    results = make_client().search_movies("A")
    assert len(results) == 1


@patch('app.clients.tmdb_client.requests.get')
def test_search_movies_returns_empty_on_failure(mock_get):
    mock_get.side_effect = requests.RequestException("network error")
    results = make_client().search_movies("A")
    assert results == []