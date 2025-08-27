import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', "db")
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

import time

def get_db_connection(retries=10, delay=2):
    """Get a pooled MySQL connection with retries."""
    for attempt in range(retries):
        try:
            conn = connection_pool.get_connection()
            return conn
        except mysql.connector.Error as e:
            print(f"DB connection failed (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Could not connect to DB after multiple attempts")
