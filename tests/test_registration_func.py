import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from DatabaseHandling.registration_func import register_user


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


# This is the most critical test fix - completely mocking the registration function
# instead of trying to mock individual SQLAlchemy components
@patch('DatabaseHandling.registration_func.User')
@patch('DatabaseHandling.registration_func.bcrypt')
@patch('DatabaseHandling.registration_func.db')
def test_register_user_success(mock_db, mock_bcrypt, mock_user_class, app):
    with app.app_context():
        # Set up our mocks
        mock_user_instance = MagicMock()
        mock_user_instance.username = "newuser"
        mock_user_instance.email = "new@example.com"
        mock_user_instance.password_hash = "hashedpassword"
        
        # Mock the User class query
        mock_user_query = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = None
        mock_user_class.query = mock_user_query
        
        # Mock User constructor
        mock_user_class.return_value = mock_user_instance
        
        # Mock bcrypt
        mock_bcrypt.generate_password_hash.return_value = b"hashedpassword"
        
        # Call the register function
        result = register_user("newuser", "new@example.com", "password")
        
        # Check the User constructor was called with the right parameters
        mock_user_class.assert_called_once()
        
        # Check db.session.add was called
        mock_db.session.add.assert_called_once()
        
        # Check db.session.commit was called
        mock_db.session.commit.assert_called_once()
        
        # Verify the result is the mocked user instance
        assert result is mock_user_instance
        assert result.username == "newuser"
        assert result.email == "new@example.com"


@patch('DatabaseHandling.registration_func.User')
@patch('DatabaseHandling.registration_func.bcrypt')
@patch('DatabaseHandling.registration_func.db')
def test_register_user_existing_user(mock_db, mock_bcrypt, mock_user_class, app):
    with app.app_context():
        # Create a mock existing user
        existing_user = MagicMock()
        existing_user.username = "testuser"
        existing_user.email = "test@example.com"
        
        # Mock the User class query to return an existing user
        mock_user_query = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = existing_user
        mock_user_class.query = mock_user_query
        
        # Call the registration function
        result = register_user("testuser", "test@example.com", "password")
        
        # Verify the result is False
        assert result is False
        
        # Verify db.session.add was not called
        mock_db.session.add.assert_not_called()
