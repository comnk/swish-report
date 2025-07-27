import mysql.connector
import os
from dotenv import load_dotenv
from fetch_rankings_current_script import fetch_247_sports_info, fetch_espn_info, fetch_rivals_info

dotenv_path = '../.env'
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

data_247 = fetch_247_sports_info(2027)
print("Successfully loaded 247 rankings")
data_espn = fetch_espn_info(2027)
print("Successfully loaded ESPN rankings")
data_rivals = fetch_rivals_info(2027)
print("Successfully loaded Rivals rankings")

cnx = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database='swish_report'
)
cursor = cnx.cursor()

insert_sql = """
INSERT INTO player_rankings
(source, class_year, player_rank, player_grade, stars, name, link, position, height, weight, school_name, city, state, location_type, is_finalized)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Insert into database
if data_247:
    cursor.executemany(insert_sql, data_247)
if data_espn:
    cursor.executemany(insert_sql, data_espn)
if data_rivals:
    cursor.executemany(insert_sql, data_rivals)

cnx.commit()

cursor.close()
cnx.close()

print("✅ Data inserted successfully!")