import pytest
from DatabaseHandling.balancecheck import get_user_balance, check_balance
from core.models import User

@pytest.fixture
def mock_user(mocker):
    user = User(email="test@example.com", balance=100.0)
    mocker.patch('core.models.User.query.filter_by', return_value=mocker.Mock(first=lambda: user))
    return user

def test_get_user_balance(mock_user):
    balance = get_user_balance("test@example.com")
    assert balance == 100.0

def test_get_user_balance_no_user(mocker):
    mocker.patch('core.models.User.query.filter_by', return_value=mocker.Mock(first=lambda: None))
    balance = get_user_balance("nonexistent@example.com")
    assert balance is None

def test_check_balance(mocker):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = (200.0,)
    mocker.patch('DatabaseHandling.balancecheck.connect_db', return_value=mocker.Mock(cursor=lambda: mock_cursor))
    balance = check_balance(1)
    assert balance == 200.0

def test_check_balance_no_result(mocker):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mocker.patch('DatabaseHandling.balancecheck.connect_db', return_value=mocker.Mock(cursor=lambda: mock_cursor))
    balance = check_balance(1)
    assert balance is None
    assert balance == None
