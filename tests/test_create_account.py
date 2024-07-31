import pytest
from flask import url_for
from flask_login import login_user
from routes.account_routes.create_account import create_account
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

def test_create_account(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.create_account"), data={
            "account_name": "Test Account",
            "account_type": "checking",
            "currency_code": "USD"
        })
        assert response.status_code == 302  # Redirects to dashboard
        assert b"Account created successfully!" in response.data

        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user.id,))
            account = cursor.fetchone()
            assert account is not None
            assert account["account_name"] == "Test Account"
            assert account["account_type"] == "checking"
            assert account["currency_code"] == "USD"

def test_create_account_invalid_currency(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.create_account"), data={
            "account_name": "Test Account",
            "account_type": "checking",
            "currency_code": "INVALID"
        })
        assert response.status_code == 400  # Bad Request
        assert b"Invalid currency code" in response.data

def test_create_account_missing_fields(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.create_account"), data={
            "account_name": "",
            "account_type": "checking",
            "currency_code": "USD"
        })
        assert response.status_code == 400  # Bad Request
        assert b"Missing required fields" in response.data

def test_create_account_duplicate_account(client, user):
    with client:
        login_user(user)
        response = client.post(url_for("account_routes.create_account"), data={
            "account_name": "Test Account",
            "account_type": "checking",
            "currency_code": "USD"
        })
        assert response.status_code == 302  # Redirects to dashboard
        assert b"Account created successfully!" in response.data

        response = client.post(url_for("account_routes.create_account"), data={
            "account_name": "Test Account",
            "account_type": "checking",
            "currency_code": "USD"
        })
        assert response.status_code == 400  # Bad Request
        assert b"Account with this name already exists" in response.data
