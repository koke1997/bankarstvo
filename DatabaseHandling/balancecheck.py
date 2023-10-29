def check_balance(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = "SELECT balance FROM Accounts WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    if result:
        return result[0]  # Return balance
    return None
