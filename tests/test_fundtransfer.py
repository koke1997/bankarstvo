import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.fundtransfer import transfer
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

def test_transfer_invalid_sender_account(mock_db):
    mock_db.fetchone.side_effect = [
        None,  # Sender's account validation
    ]

    result = transfer(999, 2, 100, 'USD')
    assert result == "Sender's account is invalid."

def test_transfer_db_error(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
        (2, 500)    # Receiver's account and balance
    ]
    mock_db.execute.side_effect = Exception("DB Error")

    result = transfer(1, 2, 100, 'USD')
    assert "An error occurred" in result
    assert "DB Error" in result

def test_transfer_same_account(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 1, 100, 'USD')
    assert result == "Cannot transfer to the same account."

def test_transfer_negative_amount(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 2, -100, 'USD')
    assert result == "Invalid transfer amount."

def test_transfer_zero_amount(mock_db):
    mock_db.fetchone.side_effect = [
        (1, 1000),  # Sender's account and balance
    ]

    result = transfer(1, 2, 0, 'USD')
    assert result == "Invalid transfer amount."
