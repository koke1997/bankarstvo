import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.fundtransfer import transfer
from flask import Flask, current_app
import os

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db():
    with patch('FiatHandling.fundtransfer.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

def test_transfer_success(mock_db, app):
    result = transfer(1, 2, 100, "USD")
    assert result == "Transfer successful"

def test_transfer_insufficient_funds(mock_db, app):
    result = transfer(1, 2, 1500, "USD")  # More than our 1000 threshold
    assert result == "Insufficient funds."

def test_transfer_invalid_currency(mock_db, app):
    result = transfer(1, 2, 100, "INVALID")
    assert result == "Invalid currency code."

def test_transfer_invalid_receiver_account(mock_db, app):
    result = transfer(1, 999, 100, "USD")
    assert result == "Receiver's account is invalid."

def test_transfer_invalid_sender_account(mock_db, app):
    result = transfer(999, 2, 100, "USD")
    assert result == "Sender's account not found."

def test_transfer_db_error(mock_db, app):
    # Set flag for DB error test
    current_app.test_db_error = True
    try:
        result = transfer(1, 2, 100, "USD")
        assert "An error occurred" in result
        assert "DB Error" in result
    finally:
        current_app.test_db_error = False

def test_transfer_same_account(mock_db, app):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 1, 100, "USD")
    assert result == "Cannot transfer to the same account."

def test_transfer_negative_amount(mock_db, app):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 2, -100, "USD")
    assert result == "Invalid transfer amount."

def test_transfer_zero_amount(mock_db, app):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 2, 0, "USD")
    assert result == "Invalid transfer amount."
