import pytest
from flask import session
from DatabaseHandling.connection import get_db_cursor
from routes.account_routes.get_balance import get_balance

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
