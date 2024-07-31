import pytest
from flask import Flask
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock
from routes.transaction_routes.stock import buy_stock, sell_stock

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_buy_stock_success(client):
    data = {
        'user_id': 1,
        'symbol': 'AAPL',
        'shares': 10
    }

    with patch('routes.transaction_routes.stock.get_user_balance', return_value=10000):
        with patch('routes.transaction_routes.stock.update_user_balance') as mock_update_balance:
            with patch('routes.transaction_routes.stock.requests.get') as mock_get:
                mock_get.return_value.json.return_value = {'price': 100}

                response = client.post('/stock/buy', json=data)
                assert response.status_code == 200
                assert response.json['message'] == 'Stock purchased successfully'
                mock_update_balance.assert_called_once()

def test_buy_stock_insufficient_balance(client):
    data = {
        'user_id': 1,
        'symbol': 'AAPL',
        'shares': 10
    }

    with patch('routes.transaction_routes.stock.get_user_balance', return_value=500):
        with patch('routes.transaction_routes.stock.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'price': 100}

            response = client.post('/stock/buy', json=data)
            assert response.status_code == 400
            assert response.json['error'] == 'Insufficient balance'

def test_sell_stock_success(client):
    data = {
        'user_id': 1,
        'symbol': 'AAPL',
        'shares': 5
    }

    with patch('routes.transaction_routes.stock.get_user_balance', return_value=10000):
        with patch('routes.transaction_routes.stock.update_user_balance') as mock_update_balance:
            with patch('routes.transaction_routes.stock.requests.get') as mock_get:
                mock_get.return_value.json.return_value = {'price': 100}
                with patch('routes.transaction_routes.stock.StockAsset.query.filter_by') as mock_query:
                    mock_asset = MagicMock()
                    mock_asset.shares = 10
                    mock_query.return_value.first.return_value = mock_asset

                    response = client.post('/stock/sell', json=data)
                    assert response.status_code == 200
                    assert response.json['message'] == 'Stock sold successfully'
                    mock_update_balance.assert_called_once()

def test_sell_stock_insufficient_balance(client):
    data = {
        'user_id': 1,
        'symbol': 'AAPL',
        'shares': 10
    }

    with patch('routes.transaction_routes.stock.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'price': 100}
        with patch('routes.transaction_routes.stock.StockAsset.query.filter_by') as mock_query:
            mock_query.return_value.first.return_value = None

            response = client.post('/stock/sell', json=data)
            assert response.status_code == 400
            assert response.json['error'] == 'Insufficient stock balance'
            assert response.json['error'] == 'Insufficient stock balance'
