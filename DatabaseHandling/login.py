from DatabaseHandling.connection import get_db_connection


def user_login(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = "SELECT password_hash, salt FROM Users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    if result:
        stored_hash, salt = result
        computed_hash = "hashed_password_here"  # Compute the hash using the provided password and stored salt
        
        if computed_hash == stored_hash:
            return True  # Successful login
    return False  # Failed login
