import pytest
from FiatHandling.accountdetails import get_account_details
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_db_connection():
    with patch('FiatHandling.accountdetails.connect_db') as mock_connect_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor

def test_get_account_details(mock_db_connection):
    user_id = 1
    expected_details = ('test_user', 'test_user@example.com', '2022-01-01', '2022-01-02')
    mock_db_connection.fetchone.return_value = expected_details

    details = get_account_details(user_id)

    assert details == expected_details
    mock_db_connection.execute.assert_called_once_with("SELECT username, email, account_created, last_login FROM Users WHERE user_id = %s", (user_id,))
    mock_db_connection.close.assert_called_once()
