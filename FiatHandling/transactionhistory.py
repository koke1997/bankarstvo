from DatabaseHandling.connection import get_db_connection


def get_transaction_history(user_id, n=10):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch the account ID for the user
    account_query = "SELECT account_id FROM Accounts WHERE user_id = %s"
    cursor.execute(account_query, (user_id,))
    result = cursor.fetchone()
    if not result:
        return None
    account_id = result[0]

    # Fetch the transaction history
    history_query = """SELECT transaction_id, from_account_id, to_account_id, amount, transaction_date, transaction_type, transaction_status, description 
                      FROM Transactions WHERE from_account_id = %s OR to_account_id = %s ORDER BY transaction_date DESC LIMIT %s"""
    cursor.execute(history_query, (account_id, account_id, n))
    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return transactions
