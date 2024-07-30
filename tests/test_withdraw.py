import pytest
from unittest.mock import patch, MagicMock
from FiatHandling.withdraw import withdraw
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
    with patch('FiatHandling.withdraw.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

def test_withdraw_success(mock_db):
    mock_db.fetchone.side_effect = [(1,), (1000,)]
    mock_db.execute.return_value = None

    result = withdraw(1, 100)
    assert result == "Withdrawal successful"
    mock_db.execute.assert_called_with("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (100, 1))

def test_withdraw_account_not_found(mock_db):
    mock_db.fetchone.side_effect = [None]

    result = withdraw(1, 100)
    assert result == "Account not found for user"

def test_withdraw_invalid_account(mock_db):
    mock_db.fetchone.side_effect = [(1,)]
    with patch('FiatHandling.withdraw.validate_account', return_value=False):
        result = withdraw(1, 100)
        assert result == "Invalid account"

def test_withdraw_insufficient_balance(mock_db):
    mock_db.fetchone.side_effect = [(1,), (50,)]

    result = withdraw(1, 100)
    assert result == "Insufficient balance for withdrawal"

def test_withdraw_db_error(mock_db):
    mock_db.execute.side_effect = Exception("DB Error")
    mock_db.fetchone.side_effect = [(1,), (1000,)]

    result = withdraw(1, 100)
    assert "An error occurred" in result
