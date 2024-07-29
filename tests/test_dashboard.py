import pytest
from flask import session, url_for
from flask_login import login_user
from routes.account_routes.dashboard import dashboard
from DatabaseHandling.connection import get_db_cursor
from app_factory import create_app
from utils.extensions import db
from core.models import User, Account

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