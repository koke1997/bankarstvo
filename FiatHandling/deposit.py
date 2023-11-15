# deposit.py

import mysql.connector
from DatabaseHandling.connection import connect_db, get_db_cursor
from validation_utils import validate_account, validate_currency

def deposit(user_id, amount, currency_code):
    """
    This function handles the deposit of funds for a user.
    """

    # Establish a database connection and get a cursor
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        # Validation
        if not validate_currency(currency_code):
            return "Invalid currency code"

        # Fetch the account_id for the given user_id and currency_code
        account_query = "SELECT account_id FROM accounts WHERE user_id = %s AND currency_code = %s"
        cursor.execute(account_query, (user_id, currency_code))
        account = cursor.fetchone()
        
        if not account:
            return "Account not found for user with given currency"
        account_id = account[0]

        if not validate_account(account_id):
            return "Invalid account ID"

        # Update the balance in the accounts table
        deposit_query = """
            UPDATE accounts
            SET balance = balance + %s
            WHERE user_id = %s AND currency_code = %s
        """
        cursor.execute(deposit_query, (amount, user_id, currency_code))
        
        # Log the deposit in the transactions table
        log_query = """
            INSERT INTO transactions (from_account_id, amount, transaction_type, description)
            VALUES (%s, %s, 'deposit', 'Deposit of funds')
        """
        cursor.execute(log_query, (account_id, amount))
        
        # Commit the database changes
        db.commit()

        return "Deposit successful"

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()  # Rollback in case of an error to avoid data inconsistencies.
        return "Failed to deposit funds"

    finally:
        # Ensure the cursor and connection are always closed
        if cursor and not cursor.closed:
            cursor.close()
        if db and db.is_connected():
            db.close()
