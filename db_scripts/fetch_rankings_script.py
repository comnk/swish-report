import mysql.connector
from playwright.sync_api import sync_playwright

import os

from dotenv import load_dotenv

dotenv_path = '../.env'

# Load the .env file
load_dotenv(dotenv_path)

# Access environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

cursorObject = cnx.cursor()