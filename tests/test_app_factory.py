import pytest
from app_factory import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_app_creation(app):
    assert app is not None
    assert app.config["TESTING"] is True

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_docs_route(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"Documentation" in response.data

def test_404_error_handler(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert b"404 Not Found" in response.data

def test_500_error_handler(client):
    with pytest.raises(Exception):
        response = client.get("/error")
        assert response.status_code == 500
        assert b"An error occurred" in response.data
