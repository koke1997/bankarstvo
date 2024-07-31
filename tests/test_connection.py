import pytest
from unittest.mock import patch, MagicMock
from DatabaseHandling.connection import connect_db, get_db_cursor
import os

@patch('DatabaseHandling.connection.pool.get_connection')
def test_connect_db(mock_get_connection):
    mock_connection = MagicMock()
    mock_get_connection.return_value = mock_connection

    connection = connect_db()

    assert connection == mock_connection
    mock_get_connection.assert_called_once()

@patch('DatabaseHandling.connection.connect_db')
def test_get_db_cursor(mock_connect_db):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_connection

    connection, cursor = get_db_cursor()

    assert connection == mock_connection
    assert cursor == mock_cursor
    mock_connect_db.assert_called_once()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    assert cursor is not None
    assert connection is not None

@patch('DatabaseHandling.connection.connect_db')
def test_get_db_cursor_with_error(mock_connect_db):
    mock_connect_db.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as excinfo:
        get_db_cursor()

    assert str(excinfo.value) == "DB Error"
    mock_connect_db.assert_called_once()

@patch('DatabaseHandling.connection.connect_db')
def test_get_db_cursor_with_custom_error(mock_connect_db):
    class CustomDBError(Exception):
        pass

    mock_connect_db.side_effect = CustomDBError("Custom DB Error")

    with pytest.raises(CustomDBError) as excinfo:
        get_db_cursor()

    assert str(excinfo.value) == "Custom DB Error"
    mock_connect_db.assert_called_once()

@patch('DatabaseHandling.connection.connect_db')
def test_get_db_cursor_with_error(mock_connect_db):
    mock_connect_db.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as excinfo:
        get_db_cursor()

    assert str(excinfo.value) == "DB Error"
    mock_connect_db.assert_called_once()

@patch('DatabaseHandling.connection.connect_db')
def test_get_db_cursor_with_custom_error(mock_connect_db):
    class CustomDBError(Exception):
        pass

    mock_connect_db.side_effect = CustomDBError("Custom DB Error")

    with pytest.raises(CustomDBError) as excinfo:
        get_db_cursor()

    assert str(excinfo.value) == "Custom DB Error"
    mock_connect_db.assert_called_once()
