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
