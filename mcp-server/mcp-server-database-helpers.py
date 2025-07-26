import mysql.connector
import os

from dotenv import load_dotenv

dotenv_path = '../.env'

load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='swish_report')
cursor = cnx.cursor()

def get_player_hs_info(player_info, hs_class_year):
    pass