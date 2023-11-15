import mysql.connector
from mysql.connector import pooling

# Initialize the connection pool
pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,  # This is the equivalent of max_connections in your original code
    pool_reset_session=True,
    host='localhost',
    port=3306,  # Port is specified separately from the host
    user='ikokalovic',
    password='Mikrovela1!',
    database='banking_app',
    charset='utf8mb4',
    autocommit=True
)

def connect_db():
    # Get a connection from the pool
    return pool.get_connection()

def get_db_cursor():
    # Get a database connection and cursor
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)  # This sets up a DictCursor
    return connection, cursor
