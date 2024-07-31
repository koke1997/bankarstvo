import pytest
from flask import session, url_for
from flask_login import login_user
from routes.account_routes.dashboard import dashboard
from DatabaseHandling.connection import get_db_cursor
from app_factory import create_app
from utils.extensions import db
from core.models import User, Account
import os

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
        ),
    })

    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def user(app):
    with app.app_context():
        user = User(username="testuser", email="testuser@example.com", password_hash="hashedpassword")
        db.session.add(user)
        db.session.commit()
        return user

def test_dashboard_access(client, user):
    with client:
        login_user(user)
        response = client.get(url_for("account_routes.dashboard"))
        assert response.status_code == 200
        assert b"Dashboard" in response.data

def test_dashboard_account_selection(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "account_choice": 1
        })
        assert response.status_code == 200
        assert session.get("selected_account_id") == 1

def test_dashboard_search(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "search_button": "search",
            "recipient": "testuser"
        })
        assert response.status_code == 200
        assert b"Search Results" in response.data

def test_dashboard_transfer(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "transfer_button": "transfer",
            "amount": 100,
            "recipient_account_id": 2
        })
        assert response.status_code == 200
        assert b"Transfer successful!" in response.data
        assert b"transactions" in response.data
        assert b"balance" in response.data

def test_dashboard_invalid_account_selection(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "account_choice": "invalid"
        })
        assert response.status_code == 400
        assert b"Invalid account selection" in response.data

def test_dashboard_no_account_selected(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "account_choice": None
        })
        assert response.status_code == 400
        assert b"No account selected" in response.data

def test_dashboard_transfer_insufficient_funds(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "transfer_button": "transfer",
            "amount": 1000000,  # Assuming this amount exceeds the user's balance
            "recipient_account_id": 2
        })
        assert response.status_code == 400
        assert b"Insufficient funds" in response.data

def test_dashboard_search_no_results(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.dashboard"), data={
            "search_button": "search",
            "recipient": "nonexistentuser"
        })
        assert response.status_code == 200
        assert b"No results found" in response.data
