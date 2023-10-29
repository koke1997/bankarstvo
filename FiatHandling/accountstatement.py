from DatabaseHandling.connection import get_db_connection

def get_monthly_statement(user_id, month, year):
    connection = get_db_connection()
    cursor = connection.cursor()

    statement_query = """SELECT transaction_id, from_account_id, to_account_id, amount, transaction_date, transaction_type, transaction_status, description 
                         FROM Transactions 
                         WHERE (from_account_id = %s OR to_account_id = %s) 
                         AND MONTH(transaction_date) = %s AND YEAR(transaction_date) = %s 
                         ORDER BY transaction_date DESC"""
    cursor.execute(statement_query, (user_id, user_id, month, year))
    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return transactions
