from DatabaseHandling.connection import get_db_connection

def withdraw(user_id, amount):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Ensure the user has sufficient funds
    balance_query = "SELECT balance FROM Accounts WHERE user_id = %s"
    cursor.execute(balance_query, (user_id,))
    result = cursor.fetchone()
    if not result or result[0] < amount:
        return "Insufficient funds"

    # Update the account balance
    withdraw_query = "UPDATE Accounts SET balance = balance - %s WHERE user_id = %s"
    cursor.execute(withdraw_query, (amount, user_id))

    # Log the transaction
    log_query = """INSERT INTO Transactions (from_account_id, amount, transaction_type, transaction_status) 
                   VALUES (%s, %s, 'Withdrawal', 'Completed')"""
    cursor.execute(log_query, (user_id, amount))

    connection.commit()
    cursor.close()
    connection.close()

    return "Withdrawal successful"
