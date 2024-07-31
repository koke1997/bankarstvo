import pytest
from flask import Flask
from flask.testing import FlaskClient
from routes.transaction_routes.crypto import crypto_routes, get_user_balance, update_user_balance
from core.models import CryptoAsset
from utils.extensions import db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(crypto_routes)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_buy_crypto(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'
    amount = 1.0

    # Mock the get_user_balance and update_user_balance functions
    def mock_get_user_balance(user_id):
        return 100000.0

    def mock_update_user_balance(user_id, new_balance):
        pass

    # Replace the real functions with the mock functions
    crypto_routes.get_user_balance = mock_get_user_balance
    crypto_routes.update_user_balance = mock_update_user_balance

    response = client.post('/crypto/buy', json={'user_id': user_id, 'symbol': symbol, 'amount': amount})
    assert response.status_code == 200
    assert response.json['message'] == 'Crypto purchased successfully'

def test_sell_crypto(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'
    amount = 1.0

    # Mock the get_user_balance and update_user_balance functions
    def mock_get_user_balance(user_id):
        return 100000.0

    def mock_update_user_balance(user_id, new_balance):
        pass

    # Replace the real functions with the mock functions
    crypto_routes.get_user_balance = mock_get_user_balance
    crypto_routes.update_user_balance = mock_update_user_balance

    # Add a crypto asset to the database
    with client.application.app_context():
        crypto_asset = CryptoAsset(user_id=user_id, symbol=symbol, balance=amount)
        db.session.add(crypto_asset)
        db.session.commit()

    response = client.post('/crypto/sell', json={'user_id': user_id, 'symbol': symbol, 'amount': amount})
    assert response.status_code == 200
    assert response.json['message'] == 'Crypto sold successfully'

def test_sell_crypto_insufficient_balance(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'
    amount = 2.0

    # Mock the get_user_balance and update_user_balance functions
    def mock_get_user_balance(user_id):
        return 100000.0

    def mock_update_user_balance(user_id, new_balance):
        pass

    # Replace the real functions with the mock functions
    crypto_routes.get_user_balance = mock_get_user_balance
    crypto_routes.update_user_balance = mock_update_user_balance

    # Add a crypto asset to the database
    with client.application.app_context():
        crypto_asset = CryptoAsset(user_id=user_id, symbol=symbol, balance=1.0)
        db.session.add(crypto_asset)
        db.session.commit()

    response = client.post('/crypto/sell', json={'user_id': user_id, 'symbol': symbol, 'amount': amount})
    assert response.status_code == 400
    assert response.json['error'] == 'Insufficient crypto balance'

def test_get_crypto_balance(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'

    # Mock the get_user_balance function
    def mock_get_user_balance(user_id):
        return 100000.0

    # Replace the real function with the mock function
    crypto_routes.get_user_balance = mock_get_user_balance

    # Add a crypto asset to the database
    with client.application.app_context():
        crypto_asset = CryptoAsset(user_id=user_id, symbol=symbol, balance=1.0)
        db.session.add(crypto_asset)
        db.session.commit()

    response = client.get(f'/crypto/balance/{user_id}/{symbol}')
    assert response.status_code == 200
    assert response.json['balance'] == 1.0

def test_get_crypto_balance_no_asset(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'

    # Mock the get_user_balance function
    def mock_get_user_balance(user_id):
        return 100000.0

    # Replace the real function with the mock function
    crypto_routes.get_user_balance = mock_get_user_balance

    response = client.get(f'/crypto/balance/{user_id}/{symbol}')
    assert response.status_code == 404
    assert response.json['error'] == 'Crypto asset not found'

def test_get_crypto_balance(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'

    # Mock the get_user_balance function
    def mock_get_user_balance(user_id):
        return 100000.0

    # Replace the real function with the mock function
    crypto_routes.get_user_balance = mock_get_user_balance

    # Add a crypto asset to the database
    with client.application.app_context():
        crypto_asset = CryptoAsset(user_id=user_id, symbol=symbol, balance=1.0)
        db.session.add(crypto_asset)
        db.session.commit()

    response = client.get(f'/crypto/balance/{user_id}/{symbol}')
    assert response.status_code == 200
    assert response.json['balance'] == 1.0

def test_get_crypto_balance_no_asset(client: FlaskClient):
    user_id = 1
    symbol = 'bitcoin'

    # Mock the get_user_balance function
    def mock_get_user_balance(user_id):
        return 100000.0

    # Replace the real function with the mock function
    crypto_routes.get_user_balance = mock_get_user_balance

    response = client.get(f'/crypto/balance/{user_id}/{symbol}')
    assert response.status_code == 404
    assert response.json['error'] == 'Crypto asset not found'
