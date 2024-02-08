# deposit.py

import mysql.connector
from DatabaseHandling.connection import connect_db, get_db_cursor
from core.validation_utils import validate_account, validate_currency
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deposit(user_id, amount, currency_code):
    """
    This function handles the deposit of funds for a user.
    """

    # Establish a database connection and get a cursor
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        logger.info(f"Attempting deposit: User ID {user_id}, Amount {amount}, Currency {currency_code}")

        # Validation
        if not validate_currency(currency_code):
            logger.warning("Invalid currency code")
            return "Invalid currency code"

        # Fetch the account_id for the given user_id and currency_code
        account_query = "SELECT account_id FROM accounts WHERE user_id = %s AND currency_code = %s"
        cursor.execute(account_query, (user_id, currency_code))
        account = cursor.fetchone()

        if not account:
            logger.warning(f"Account not found for user {user_id} with currency {currency_code}")
            return "Account not found for user with given currency"
        account_id = account[0]

        if not validate_account(account_id):
            logger.warning(f"Invalid account: Account ID {account_id}")
            return "Invalid account"

        # Update balance
        update_query = "UPDATE accounts SET balance = balance + %s WHERE account_id = %s"
        cursor.execute(update_query, (amount, account_id))
        db.commit()

        logger.info(f"Deposit successful: User ID {user_id}, Amount {amount}, Currency {currency_code}")

        return "Deposit successful"

    except mysql.connector.Error as err:
        logger.error(f"Error during deposit: {err}")
        db.rollback()
        return f"An error occurred: {err}"
    finally:
        cursor.close()
        db.close()
