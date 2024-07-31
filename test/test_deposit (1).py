import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from FiatHandling.deposit import deposit

class TestDeposit(unittest.TestCase):
    @patch('FiatHandling.deposit.connect_db')
    @patch('FiatHandling.deposit.get_db_cursor')
    @patch('FiatHandling.deposit.validate_currency')
    @patch('FiatHandling.deposit.validate_account')
    def test_successful_deposit(self, mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_get_db_cursor.return_value = mock_cursor

        # Mock account validation
        mock_validate_currency.return_value = True
        mock_validate_account.return_value = True

        # Mock database fetch and update operations
        mock_cursor.fetchone.return_value = [1]  # Mock account_id
        mock_cursor.execute.return_value = True
        mock_conn.commit.return_value = True

        response = deposit('valid_user', 100, 'USD')
        self.assertEqual(response, "Deposit successful")

    @patch('FiatHandling.deposit.connect_db')
    @patch('FiatHandling.deposit.get_db_cursor')
    @patch('FiatHandling.deposit.validate_currency')
    def test_invalid_currency(self, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_get_db_cursor.return_value = mock_cursor

        # Mock invalid currency validation
        mock_validate_currency.return_value = False

        response = deposit('valid_user', 100, 'INVALID')
        self.assertEqual(response, "Invalid currency code")

    @patch('FiatHandling.deposit.connect_db')
    @patch('FiatHandling.deposit.get_db_cursor')
    @patch('FiatHandling.deposit.validate_currency')
    def test_account_not_found(self, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_get_db_cursor.return_value = mock_cursor

        # Mock valid currency validation
        mock_validate_currency.return_value = True

        # Mock account not found
        mock_cursor.fetchone.return_value = None

        response = deposit('valid_user', 100, 'USD')
        self.assertEqual(response, "Account not found for user with given currency")

    @patch('FiatHandling.deposit.connect_db')
    @patch('FiatHandling.deposit.get_db_cursor')
    @patch('FiatHandling.deposit.validate_currency')
    @patch('FiatHandling.deposit.validate_account')
    def test_invalid_account(self, mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_get_db_cursor.return_value = mock_cursor

        # Mock valid currency validation
        mock_validate_currency.return_value = True

        # Mock account validation
        mock_validate_account.return_value = False

        # Mock database fetch operation
        mock_cursor.fetchone.return_value = [1]  # Mock account_id

        response = deposit('valid_user', 100, 'USD')
        self.assertEqual(response, "Invalid account")

    @patch('FiatHandling.deposit.connect_db')
    @patch('FiatHandling.deposit.get_db_cursor')
    @patch('FiatHandling.deposit.validate_currency')
    @patch('FiatHandling.deposit.validate_account')
    def test_database_error(self, mock_validate_account, mock_validate_currency, mock_get_db_cursor, mock_connect_db):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_get_db_cursor.return_value = mock_cursor

        # Mock account validation
        mock_validate_currency.return_value = True
        mock_validate_account.return_value = True

        # Mock database fetch and update operations
        mock_cursor.fetchone.return_value = [1]  # Mock account_id
        mock_cursor.execute.side_effect = Exception("DB Error")

        response = deposit('valid_user', 100, 'USD')
        self.assertIn("An error occurred", response)

if __name__ == '__main__':
    unittest.main()
