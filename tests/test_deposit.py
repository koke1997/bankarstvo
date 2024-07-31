import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.deposit import deposit
import os

@pytest.fixture
def mock_db():
    with patch('FiatHandling.deposit.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

def test_deposit_success(mock_db):
    mock_db.fetchone.side_effect = [(1,), (1,)]
    mock_db.execute.return_value = None

    result = deposit(1, 100, 'USD')
    assert result == "Deposit successful"
    mock_db.execute.assert_called_with("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (100, 1))

def test_deposit_invalid_currency(mock_db):
    with patch('FiatHandling.deposit.validate_currency', return_value=False):
        result = deposit(1, 100, 'INVALID')
        assert result == "Invalid currency code"

def test_deposit_account_not_found(mock_db):
    mock_db.fetchone.side_effect = [None]

    result = deposit(1, 100, 'USD')
    assert result == "Account not found for user with given currency"

def test_deposit_invalid_account(mock_db):
    mock_db.fetchone.side_effect = [(1,)]
    with patch('FiatHandling.deposit.validate_account', return_value=False):
        result = deposit(1, 100, 'USD')
        assert result == "Invalid account"

def test_deposit_db_error(mock_db):
    mock_db.execute.side_effect = Exception("DB Error")
    mock_db.fetchone.side_effect = [(1,), (1,)]

    result = deposit(1, 100, 'USD')
    assert "An error occurred" in result
    assert "DB Error" in result

