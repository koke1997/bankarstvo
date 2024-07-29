import pytest
from flask import Flask, session
from flask.testing import FlaskClient
from routes.transaction_routes.transfer import transfer
from DatabaseHandling.connection import get_db_cursor
import os

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME')
    )
    app.register_blueprint(transfer)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_transfer_success(client: FlaskClient):
    with client.session_transaction() as sess:
        sess['selected_account_id'] = 1

    data = {
        'amount': 100.0,
        'recipient_account_id': 2
    }

    with patch('routes.transaction_routes.transfer.get_db_cursor') as mock_get_db_cursor:
        mock_cursor = MagicMock()
        mock_get_db_cursor.return_value = (MagicMock(), mock_cursor)
        mock_cursor.fetchone.side_effect = [{'balance': 200.0}, {'balance': 100.0}]

        response = client.post('/transfer', data=data)
        assert response.status_code == 200
        assert b'Transfer successful!' in response.data

def test_transfer_insufficient_balance(client: FlaskClient):
    with client.session_transaction() as sess:
        sess['selected_account_id'] = 1

    data = {
        'amount': 300.0,
        'recipient_account_id': 2
    }

    with patch('routes.transaction_routes.transfer.get_db_cursor') as mock_get_db_cursor:
        mock_cursor = MagicMock()
        mock_get_db_cursor.return_value = (MagicMock(), mock_cursor)
        mock_cursor.fetchone.side_effect = [{'balance': 200.0}, {'balance': 100.0}]

        response = client.post('/transfer', data=data)
        assert response.status_code == 200
        assert b'Insufficient balance for transfer!' in response.data

def test_transfer_invalid_recipient_account(client: FlaskClient):
    with client.session_transaction() as sess:
        sess['selected_account_id'] = 1

    data = {
        'amount': 100.0,
        'recipient_account_id': 'invalid'
    }

    response = client.post('/transfer', data=data)
    assert response.status_code == 200
    assert b'Invalid recipient account ID' in response.data

def test_transfer_invalid_amount(client: FlaskClient):
    with client.session_transaction() as sess:
        sess['selected_account_id'] = 1

    data = {
        'amount': 'invalid',
        'recipient_account_id': 2
    }

    response = client.post('/transfer', data=data)
    assert response.status_code == 200
    assert b'Invalid transfer amount' in response.data
