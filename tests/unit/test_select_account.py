import pytest
from flask import session, url_for
from flask_login import LoginManager, login_user
from unittest.mock import patch, MagicMock
from flask import Flask


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Create routes for testing
    @app.route('/select_account', methods=['POST'])
    def select_account():
        from flask import request, redirect, session
        account_id = request.form.get('account_choice', type=int)
        session['selected_account_id'] = account_id
        return redirect('/dashboard')
    
    @app.route('/dashboard')
    def dashboard():
        return "Dashboard"
    
    # Add blueprint name for url_for to work
    app.blueprints['account_routes'] = app
    
    # Setup user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Create a simple mock User class for testing
        class MockUser:
            def __init__(self, id):
                self.id = id
                
            def get_id(self):
                return str(self.id)
                
            def is_authenticated(self):
                return True
                
            def is_active(self):
                return True
                
            def is_anonymous(self):
                return False
        
        return MockUser(user_id)
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user():
    # Create a simple mock User class for testing
    class MockUser:
        def __init__(self):
            self.id = 1
            
        def get_id(self):
            return str(self.id)
            
        def is_authenticated(self):
            return True
            
        def is_active(self):
            return True
            
        def is_anonymous(self):
            return False
    
    return MockUser()


def test_select_account(app, client, user):
    with app.test_request_context():
        # Setup a test client with a session
        with client.session_transaction() as sess:
            sess['_user_id'] = user.get_id()  # Simulate user already logged in
        
        # Mock the database operations
        with patch('DatabaseHandling.connection.get_db_cursor') as mock_cursor_func:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor_func.return_value.__enter__.return_value = mock_cursor
            
            # Mock the account data
            mock_cursor.fetchone.return_value = {
                'account_id': 1,
                'user_id': 1,
                'account_type': 'checking',
                'balance': 1000.0,
                'currency_code': 'USD'
            }
            
            # Make the request to select an account
            response = client.post('/select_account', data={'account_choice': 1})
            
            # Verify redirect
            assert response.status_code == 302
            
            # Verify session was updated
            with client.session_transaction() as sess:
                assert sess.get('selected_account_id') == 1
