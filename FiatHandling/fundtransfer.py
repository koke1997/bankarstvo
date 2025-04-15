import mysql.connector
from DatabaseHandling.connection import connect_db, get_db_cursor
from core.validation_utils import validate_account, validate_currency
import logging

logger = logging.getLogger(__name__)


def transfer(sender_user_id, receiver_account_id, amount, currency_code):
    """
    Transfer funds from sender to receiver.
    """

    # Establish a database connection and get a cursor
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        # Validate currency code
        if not validate_currency(currency_code):
            return "Invalid currency code."

        # Fetch the sender's account_id using sender_user_id and currency_code
        sender_query = (
            "SELECT account_id, balance FROM accounts WHERE user_id = %s AND currency_code = %s"
        )
        cursor.execute(sender_query, (sender_user_id, currency_code))
        sender_account = cursor.fetchone()

        if not sender_account:
            return "Sender's account not found."

        sender_account_id, sender_balance = sender_account

        # Check if the sender has sufficient funds
        if sender_balance < amount:
            return "Insufficient funds."

        # Check if the receiver's account is valid
        if not validate_account(receiver_account_id):
            return "Receiver's account is invalid."

        # Transfer funds: Deduct from sender and add to receiver
        deduct_query = """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_id = %s
        """
        cursor.execute(deduct_query, (amount, sender_account_id))

        add_query = """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_id = %s
        """
        cursor.execute(add_query, (amount, receiver_account_id))

        # Log the transaction
        log_query = """
            INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description)
            VALUES (%s, %s, %s, 'transfer', 'Fund transfer')
        """
        cursor.execute(log_query, (sender_account_id, receiver_account_id, amount))

        # Commit the database changes
        db.commit()

        return "Transfer successful"

    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        return "Failed to transfer funds"

    finally:
        # Ensure the cursor and connection are always closed
        if cursor and not cursor.closed:
            cursor.close()
        if db and db.is_connected():
            db.close()
