import pytest
from flask import session, url_for
from flask_login import login_user
from routes.account_routes.select_account import select_account
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

def test_select_account(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.select_account"), data={
            "account_choice": 1
        })
        assert response.status_code == 302  # Redirects to dashboard
        assert session.get("selected_account_id") == 1

        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (1,))
            account = cursor.fetchone()
            assert account is not None
            assert account["account_id"] == 1
