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
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash="hashedpassword",
        )
        db.session.add(user)
        db.session.commit()
        # Create a valid account for the user (only valid fields)
        account = Account(
            account_type="checking",
            balance=1000.00,
            currency_code="USD",
            user_id=user.user_id
        )
        db.session.add(account)
        db.session.commit()
        return db.session.get(User, user.user_id)


@pytest.fixture(autouse=True)
def patch_login_route(monkeypatch, app):
    """Patch the /login route to always log in the test user for tests."""
    from flask_login import login_user
    from core.models import User
    
    def fake_login():
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            login_user(user)
        return "Logged in for test!"
    app.view_functions["user_routes.login"] = fake_login


def login_test_user(client, app):
    with app.app_context():
        from core.models import User
        user = User.query.filter_by(username="testuser").first()
        # Set session variables for the test
        with client.session_transaction() as sess:
            sess['user_id'] = user.user_id
            sess['_fresh'] = True
    # Get the login page to trigger the fake_login function
    client.get("/login", follow_redirects=True)


def test_create_account(client, app, user):
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()
    login_test_user(client, app)
    response = client.post(
        "/create_account",
        data={
            "account_type": "checking",
            "currency_code": "USD",
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Account created successfully!" in response.data

    # Use SQLAlchemy instead of raw database connection
    with app.app_context():
        account = Account.query.filter_by(user_id=user.user_id, account_type="checking", currency_code="USD").first()
        assert account is not None
        assert account.account_type == "checking"
        assert account.currency_code == "USD"


def test_create_account_invalid_currency(client, app, user):
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()
    login_test_user(client, app)
    response = client.post(
        "/create_account",
        data={
            "account_type": "checking",
            "currency_code": "INVALID",
        },
    )
    assert response.status_code == 400  # Bad Request
    assert b"Invalid currency code" in response.data


def test_create_account_missing_fields(client, app, user):
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()
    login_test_user(client, app)
    response = client.post(
        "/create_account",
        data={
            # Both fields missing
        },
    )
    assert response.status_code == 400  # Bad Request
    assert b"Missing required fields" in response.data


def test_create_account_duplicate_account(client, app, user):
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()
    login_test_user(client, app)
    response = client.post(
        "/create_account",
        data={
            "account_type": "checking",
            "currency_code": "USD",
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Account created successfully!" in response.data

    response = client.post(
        "/create_account",
        data={
            "account_type": "checking",
            "currency_code": "USD",
        },
        follow_redirects=True
    )
    assert response.status_code == 400  # Duplicate should fail
    assert b"Account with this type and currency already exists" in response.data
