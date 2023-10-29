from DatabaseHandling.connection import get_db_connection

def transfer_funds(from_user_id, to_account_id, amount):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Ensure the "from" user has sufficient funds
    balance_query = "SELECT balance FROM Accounts WHERE user_id = %s"
    cursor.execute(balance_query, (from_user_id,))
    result = cursor.fetchone()
    if not result or result[0] < amount:
        return "Insufficient funds"

    # Update the "from" account
    debit_query = "UPDATE Accounts SET balance = balance - %s WHERE user_id = %s"
    cursor.execute(debit_query, (amount, from_user_id))

    # Update the "to" account
    credit_query = "UPDATE Accounts SET balance = balance + %s WHERE account_id = %s"
    cursor.execute(credit_query, (amount, to_account_id))

    # Log the transaction
    log_query = """INSERT INTO Transactions (from_account_id, to_account_id, amount, transaction_type, transaction_status) 
                   VALUES (%s, %s, %s, 'Transfer', 'Completed')"""
    cursor.execute(log_query, (from_user_id, to_account_id, amount))

    connection.commit()
    cursor.close()
    connection.close()

    return "Transfer successful"
