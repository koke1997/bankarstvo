import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.fundtransfer import transfer

@pytest.fixture
def mock_db():
    with patch('FiatHandling.fundtransfer.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

def test_transfer_success(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
        None,       # Receiver's account validation
        None        # Log transaction
    ]

    result = transfer(1, 2, 100, 'USD')
    assert result == "Transfer successful"
    mock_db.execute.assert_any_call("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (100, 1))
    mock_db.execute.assert_any_call("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (100, 2))

def test_transfer_insufficient_funds(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 50),  # Sender's account and balance
    ]

    result = transfer(1, 2, 100, 'USD')
    assert result == "Insufficient funds"

def test_transfer_invalid_currency(mock_db):
    result = transfer(1, 2, 100, 'INVALID')
    assert result == "Invalid currency code."

def test_transfer_invalid_receiver_account(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
        None        # Receiver's account validation
    ]

    result = transfer(1, 999, 100, 'USD')
    assert result == "Receiver's account is invalid."
