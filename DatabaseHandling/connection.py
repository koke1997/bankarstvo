import mysql.connector

def get_db_connection():
    config = {
        'host': 'localhost',
        'user': 'ivank',
        'password': 'Mikrovela1!',
        'database': 'banking_app'
    }
    connection = mysql.connector.connect(**config)
    return connection

def get_db_cursor(connection):
    return connection.cursor(buffered=True)