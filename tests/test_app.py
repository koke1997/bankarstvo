import pytest
from flask import Flask
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

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Banking App" in response.data

def test_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"Documentation" in response.data

def test_404(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert b"404 Not Found" in response.data

def test_error_handler(client):
    response = client.get("/error")
    assert response.status_code == 500
    assert b"An error occurred" in response.data
    assert b"Error" in response.data
    assert b"500" in response.data

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

def test_app_config(app):
    assert app.config["DEBUG"] is False
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

def test_app_routes(client):
    response = client.get("/api/v1/resource")
    assert response.status_code == 200
    assert b"Resource data" in response.data

def test_app_error_handling(client):
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    assert b"Not Found" in response.data

def test_app_logging(app):
    with app.app_context():
        app.logger.info("Test log message")
        assert "Test log message" in app.logger.handlers[0].stream.getvalue()
