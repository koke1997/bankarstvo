import mysql.connector
from mysql.connector import pooling
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        connection = pool.get_connection()
        logger.info("Database connection established")
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to the database: {err}")
        raise

def get_db_cursor():
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        logger.info("Database cursor obtained")
        return connection, cursor
    except mysql.connector.Error as err:
        logger.error(f"Error getting database cursor: {err}")
        raise