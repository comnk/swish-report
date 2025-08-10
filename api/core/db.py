import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME', 'swish_report')

# Create a connection pool to reuse connections
connection_pool = pooling.MySQLConnectionPool(
    pool_name="swish_pool",
    pool_size=10,
    pool_reset_session=True,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

def get_db_connection():
    """Get a pooled MySQL connection."""
    return connection_pool.get_connection()
