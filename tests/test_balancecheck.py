import pytest
from DatabaseHandling.balancecheck import get_user_balance, check_balance
from core.models import Account, User
from unittest.mock import patch, MagicMock
from app_factory import create_app
from utils.extensions import db


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        from utils.extensions import db
        db.create_all()
        yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def mock_account(mocker, app):
    account = Account()
    account.balance = 100.0
    # Updated to mock db.session.query instead of Account.query
    query_mock = mocker.Mock()
    join_mock = mocker.Mock()
    filter_mock = mocker.Mock()
    first_mock = mocker.Mock(return_value=account)
    
    filter_mock.first = first_mock
    join_mock.filter_by = lambda email: filter_mock
    query_mock.join = lambda User: join_mock
    
    mocker.patch("utils.extensions.db.session.query", return_value=query_mock)
    return account


@pytest.fixture
def user(app):
    with app.app_context():
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash="hashedpassword",
        )
        db.session.add(user)
        db.session.commit()
        return db.session.get(User, user.user_id)


def test_get_user_balance(mock_account, app):
    with app.app_context():
        from core.models import Account, User
        user = User(username="testuser2", email="test2@example.com", password_hash="pw")
        db.session.add(user)
        db.session.commit()
        account = Account(
            account_type="checking", 
            balance=100.0, 
            currency_code="USD", 
            user_id=user.user_id,
            status="active"  # Added required field
        )
        db.session.add(account)
        db.session.commit()
        balance = get_user_balance(user.email)
        assert balance == 100.0


def test_get_user_balance_no_user(mocker, app):
    # Updated to mock db.session.query instead of Account.query
    query_mock = mocker.Mock()
    join_mock = mocker.Mock()
    filter_mock = mocker.Mock()
    first_mock = mocker.Mock(return_value=None)
    
    filter_mock.first = first_mock
    join_mock.filter_by = lambda email: filter_mock
    query_mock.join = lambda User: join_mock
    
    mocker.patch("utils.extensions.db.session.query", return_value=query_mock)
    
    with app.app_context():
        balance = get_user_balance("nonexistent@example.com")
        assert balance is None


def test_check_balance(mocker, app):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = (200.0,)
    mocker.patch(
        "DatabaseHandling.balancecheck.connect_db",
        return_value=mocker.Mock(cursor=lambda: mock_cursor),
    )
    with app.app_context():
        balance = check_balance(1)
        assert balance == 200.0


def test_check_balance_no_result(mocker, app):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mocker.patch(
        "DatabaseHandling.balancecheck.connect_db",
        return_value=mocker.Mock(cursor=lambda: mock_cursor),
    )
    with app.app_context():
        balance = check_balance(1)
        assert balance is None


def test_check_balance_invalid_user(mocker, app):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mocker.patch(
        "DatabaseHandling.balancecheck.connect_db",
        return_value=mocker.Mock(cursor=lambda: mock_cursor),
    )
    with app.app_context():
        balance = check_balance(999)
        assert balance is None


def test_check_balance_db_error(mocker, app):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.side_effect = Exception("DB Error")
    mocker.patch(
        "DatabaseHandling.balancecheck.connect_db",
        return_value=mocker.Mock(cursor=lambda: mock_cursor),
    )
    with app.app_context():
        with pytest.raises(Exception) as excinfo:
            check_balance(1)
        assert str(excinfo.value) == "DB Error"
