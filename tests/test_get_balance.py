import pytest
from flask import session
from DatabaseHandling.connection import get_db_cursor
from routes.account_routes.get_balance import get_balance
import os
from app_factory import create_app
from utils.extensions import db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_balance(client):
    with client.session_transaction() as sess:
        sess["selected_account_id"] = 1

    response = client.get("/get_balance")
    assert response.status_code == 200
    assert "balance" in response.json
    assert response.json["balance"] == 100.00  # Replace with the expected balance for account_id 1

def test_get_balance_no_account_selected(client):
    response = client.get("/get_balance")
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "No account selected"

def test_get_balance_invalid_account(client):
    with client.session_transaction() as sess:
        sess["selected_account_id"] = 999  # Assuming 999 is an invalid account_id

    response = client.get("/get_balance")
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Invalid account"

def test_get_balance_db_error(client, mocker):
    # Set a flag to trigger the DB error in test mode
    client.application.test_db_error = True
    
    with client.session_transaction() as sess:
        sess["selected_account_id"] = 1

    try:
        response = client.get("/get_balance")
        assert response.status_code == 500
        assert "error" in response.json
        assert response.json["error"] == "An error occurred while fetching the balance"
    finally:
        # Remove the flag
        client.application.test_db_error = False
