# withdraw.py

import mysql.connector
from DatabaseHandling.connection import connect_db, get_db_cursor
from validation_utils import validate_account
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def withdraw(user_id, amount):
    """
    This function handles the withdrawal of funds for a user.
    """

    # Establish a database connection and get a cursor
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        logger.info(f"Attempting withdrawal: User ID {user_id}, Amount {amount}")

        # Fetch the account_id for the given user_id
        account_query = "SELECT account_id FROM accounts WHERE user_id = %s"
        cursor.execute(account_query, (user_id,))
        account = cursor.fetchone()

        if not account:
            logger.warning(f"Account not found for user {user_id}")
            return "Account not found for user"

        account_id = account[0]

        if not validate_account(account_id):
            logger.warning(f"Invalid account: Account ID {account_id}")
            return "Invalid account"

        # Check if the user has sufficient funds
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
        balance = cursor.fetchone()[0]

        if balance < amount:
            logger.warning(
                f"Insufficient balance for withdrawal: User ID {user_id}, Balance {balance}, Amount {amount}"
            )
            return "Insufficient balance for withdrawal"

        # Update balance
        update_query = "UPDATE accounts SET balance = balance - %s WHERE account_id = %s"
        cursor.execute(update_query, (amount, account_id))

        # Log the transaction
        log_query = """INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                       VALUES (%s, %s, 'withdrawal', 'Withdrawal from account')"""
        cursor.execute(log_query, (account_id, amount))

        db.commit()
        logger.info(f"Withdrawal successful: User ID {user_id}, Amount {amount}")

        return "Withdrawal successful"

    except mysql.connector.Error as err:
        logger.error(f"Error during withdrawal: {err}")
        db.rollback()
        return f"An error occurred: {err}"
    finally:
        cursor.close()
        db.close()
