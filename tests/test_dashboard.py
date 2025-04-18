import pytest
from flask import session
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

def login_test_user(client):
    # Get the app from the client
    app = client.application
    with app.app_context():
        from core.models import User
        user = User.query.filter_by(username="testuser").first()
        # Set session variables for the test
        with client.session_transaction() as sess:
            sess['user_id'] = user.user_id
            sess['_fresh'] = True
    # Get the login page to trigger the fake_login function
    return client.get("/login", follow_redirects=True)

def test_dashboard_access(client, user):
    login_test_user(client)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_dashboard_account_selection(client, user):
    login_test_user(client)
    with client.session_transaction() as sess:
        # Clear any existing session data
        if 'selected_account_id' in sess:
            del sess['selected_account_id']
            
    # Now post to dashboard to select an account
    response = client.post("/dashboard", data={
        "account_choice": 1
    })
    assert response.status_code == 200
    
    # Check session values using the client's session
    with client.session_transaction() as sess:
        assert sess.get("selected_account_id") == '1'  # Note: session values are stored as strings

def test_dashboard_search(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "search_button": "search",
        "recipient": "testuser"
    })
    assert response.status_code == 200
    assert b"Search Results" in response.data

def test_dashboard_transfer(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "transfer_button": "transfer",
        "amount": 100,
        "recipient_account_id": 2
    })
    assert response.status_code == 200
    assert b"Transfer successful!" in response.data
    assert b"transactions" in response.data
    assert b"balance" in response.data

def test_dashboard_invalid_account_selection(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "account_choice": "invalid"
    })
    assert response.status_code == 400
    assert b"Invalid account selection" in response.data

def test_dashboard_no_account_selected(client, user):
    login_test_user(client)
    # Use string 'None' instead of Python None value
    response = client.post("/dashboard", data={
        "account_choice": 'None'
    })
    assert response.status_code == 400
    assert b"No account selected" in response.data

def test_dashboard_transfer_insufficient_funds(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "transfer_button": "transfer",
        "amount": 1000000,  # Assuming this amount exceeds the user's balance
        "recipient_account_id": 2
    })
    assert response.status_code == 400
    assert b"Insufficient funds" in response.data

def test_dashboard_search(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "search_button": "search",
        "recipient": "testuser"
    })
    assert response.status_code == 200
    assert b"Search Results" in response.data

def test_dashboard_search_no_results(client, user):
    login_test_user(client)
    response = client.post("/dashboard", data={
        "search_button": "search",
        "recipient": "nonexistentuser"
    })
    assert response.status_code == 200
    assert b"No results found" in response.data
