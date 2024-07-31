import pytest
from unittest.mock import patch, MagicMock
from DatabaseHandling.registration_func import register_user
from core.models import User

@pytest.fixture
def mock_user(mocker):
    user = User(username="testuser", email="test@example.com", password_hash="hashedpassword")
    mocker.patch('core.models.User.query.filter_by', return_value=mocker.Mock(first=lambda: user))
    return user

def test_register_user_success(mocker):
    mocker.patch('core.models.User.query.filter_by', return_value=mocker.Mock(first=lambda: None))
    mocker.patch('utils.extensions.db.session.add')
    mocker.patch('utils.extensions.db.session.commit')
    mocker.patch('utils.extensions.bcrypt.generate_password_hash', return_value="hashedpassword")

    new_user = register_user("newuser", "new@example.com", "password")
    assert new_user.username == "newuser"
    assert new_user.email == "new@example.com"
    assert new_user.password_hash == "hashedpassword"

def test_register_user_existing_user(mock_user):
    result = register_user("testuser", "test@example.com", "password")
    assert result is False
    assert mock_user.username == "testuser"
    assert mock_user.email == "test@example.com"
