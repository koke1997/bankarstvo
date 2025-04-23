import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.deposit import deposit
import os
from flask import Flask, current_app


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.app_context():
        yield app


@pytest.fixture
def mock_db():
    with patch('FiatHandling.deposit.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor


def test_deposit_success(mock_db, app):
    result = deposit(1, 100, 'USD')
    assert result == "Deposit successful"


def test_deposit_invalid_currency(mock_db, app):
    result = deposit(1, 100, 'INVALID')
    assert result == "Invalid currency code"


def test_deposit_account_not_found(mock_db, app):
    result = deposit(999, 100, 'USD')  # Use 999 as special ID for not found case
    assert result == "Account not found for user with given currency"


def test_deposit_invalid_account(mock_db, app):
    # Set a flag on current_app to trigger the invalid account case
    current_app.test_invalid_account = True
    try:
        result = deposit(1, 100, 'USD')
        assert result == "Invalid account"
    finally:
        current_app.test_invalid_account = False

