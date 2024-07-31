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

@patch('FiatHandling.deposit.connect_db')
@patch('FiatHandling.deposit.get_db_cursor')
@patch('FiatHandling.deposit.validate_currency')
@patch('FiatHandling.deposit.validate_account')
def test_successful_deposit(mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_get_db_cursor.return_value = mock_cursor

    # Mock account validation
    mock_validate_currency.return_value = True
    mock_validate_account.return_value = True

    # Mock database fetch and update operations
    mock_cursor.fetchone.return_value = [1]  # Mock account_id
    mock_cursor.execute.return_value = True
    mock_conn.commit.return_value = True

    response = deposit('valid_user', 100, 'USD')
    assert response == "Deposit successful"

@patch('FiatHandling.deposit.connect_db')
@patch('FiatHandling.deposit.get_db_cursor')
@patch('FiatHandling.deposit.validate_currency')
def test_invalid_currency(mock_validate_currency, mock_get_db_cursor, mock_connect_db):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_get_db_cursor.return_value = mock_cursor

    # Mock invalid currency validation
    mock_validate_currency.return_value = False

    response = deposit('valid_user', 100, 'INVALID')
    assert response == "Invalid currency code"

@patch('FiatHandling.deposit.connect_db')
@patch('FiatHandling.deposit.get_db_cursor')
@patch('FiatHandling.deposit.validate_currency')
def test_account_not_found(mock_validate_currency, mock_get_db_cursor, mock_connect_db):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_get_db_cursor.return_value = mock_cursor

    # Mock valid currency validation
    mock_validate_currency.return_value = True

    # Mock account not found
    mock_cursor.fetchone.return_value = None

    response = deposit('valid_user', 100, 'USD')
    assert response == "Account not found for user with given currency"

@patch('FiatHandling.deposit.connect_db')
@patch('FiatHandling.deposit.get_db_cursor')
@patch('FiatHandling.deposit.validate_currency')
@patch('FiatHandling.deposit.validate_account')
def test_invalid_account(mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_get_db_cursor.return_value = mock_cursor

    # Mock valid currency validation
    mock_validate_currency.return_value = True

    # Mock account validation
    mock_validate_account.return_value = False

    # Mock database fetch operation
    mock_cursor.fetchone.return_value = [1]  # Mock account_id

    response = deposit('valid_user', 100, 'USD')
    assert response == "Invalid account"

@patch('FiatHandling.deposit.connect_db')
@patch('FiatHandling.deposit.get_db_cursor')
@patch('FiatHandling.deposit.validate_currency')
@patch('FiatHandling.deposit.validate_account')
def test_database_error(mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_get_db_cursor.return_value = mock_cursor

    # Mock account validation
    mock_validate_currency.return_value = True
    mock_validate_account.return_value = True

    # Mock database fetch and update operations
    mock_cursor.fetchone.return_value = [1]  # Mock account_id
    mock_cursor.execute.side_effect = Exception("DB Error")

    response = deposit('valid_user', 100, 'USD')
    assert "An error occurred" in response
