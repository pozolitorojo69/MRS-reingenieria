from unittest.mock import patch


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_unknown_route_returns_404(client):
    response = client.get('/api/does-not-exist')
    assert response.status_code == 404


@patch('app.blueprints.api.routes.tmdb_client')
def test_movie_details_not_found_returns_404(mock_tmdb, client):
    mock_tmdb.get_movie.return_value = None
    response = client.get('/api/movie/999')
    assert response.status_code == 404
    assert response.get_json() == {'error': 'Movie not found'}


@patch('app.blueprints.api.routes.tmdb_client')
def test_movie_details_found_returns_200(mock_tmdb, client):
    mock_tmdb.get_movie.return_value = {'id': 1, 'title': 'Inception'}
    response = client.get('/api/movie/1')
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Inception'


@patch('app.blueprints.api.routes.service')
def test_recommendations_uses_filters_path_without_title(mock_service, client):
    mock_service.recommend_by_filters.return_value = [{'id': 1, 'title': 'X'}]
    response = client.get('/api/recommendations?genre=Action')
    assert response.status_code == 200
    assert response.get_json() == [{'id': 1, 'title': 'X'}]
    mock_service.recommend_by_filters.assert_called_once()


@patch('app.blueprints.api.routes.service')
def test_recommendations_uses_title_path_when_title_given(mock_service, client):
    mock_service.recommend_by_title.return_value = []
    response = client.get('/api/recommendations?title=Inception')
    assert response.status_code == 200
    mock_service.recommend_by_title.assert_called_once()