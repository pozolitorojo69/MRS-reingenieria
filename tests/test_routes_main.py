def test_index_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200