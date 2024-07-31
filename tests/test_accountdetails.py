import pytest
from FiatHandling.accountdetails import get_account_details
from unittest.mock import patch, MagicMock
from flask_sqlalchemy import SQLAlchemy
from app_factory import create_app


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope="module")
def init_database():
    db = SQLAlchemy()
    db.create_all()

    yield db

    db.session.remove()
    db.drop_all()


@pytest.fixture
def mock_db_connection():
    with patch("FiatHandling.accountdetails.connect_db") as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor


def test_get_account_details(mock_db_connection):
    user_id = 1
    expected_details = (
        "test_user",
        "test_user@example.com",
        "2022-01-01",
        "2022-01-02",
    )
    mock_db_connection.fetchone.return_value = expected_details

    details = get_account_details(user_id)

    assert details == expected_details
    mock_db_connection.execute.assert_called_once_with(
        "SELECT username, email, account_created, last_login FROM Users WHERE user_id = %s",
        (user_id,),
    )
    mock_db_connection.close.assert_called_once()
    assert details[0] == "test_user"
    assert details[1] == "test_user@example.com"
    assert details[2] == "2022-01-01"
    assert details[3] == "2022-01-02"


def test_get_account_details_invalid_user(mock_db_connection):
    user_id = 999
    mock_db_connection.fetchone.return_value = None

    details = get_account_details(user_id)

    assert details is None
    mock_db_connection.execute.assert_called_once_with(
        "SELECT username, email, account_created, last_login FROM Users WHERE user_id = %s",
        (user_id,),
    )
    mock_db_connection.close.assert_called_once()


def test_get_account_details_db_error(mock_db_connection):
    user_id = 1
    mock_db_connection.execute.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as excinfo:
        get_account_details(user_id)

    assert str(excinfo.value) == "DB Error"
    mock_db_connection.execute.assert_called_once_with(
        "SELECT username, email, account_created, last_login FROM Users WHERE user_id = %s",
        (user_id,),
    )
    mock_db_connection.close.assert_called_once()
