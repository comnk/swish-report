import mysql.connector
import os
from dotenv import load_dotenv
from fetch_rankings_current_script import fetch_247_sports_info, fetch_espn_info, fetch_rivals_info
from db_script_helper_functions import find_matching_player

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

rankings = data_247 + data_espn + data_rivals

cnx = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database='swish_report'
)
cursor = cnx.cursor()

insert_rank_sql = """
INSERT INTO high_school_player_rankings
(player_uid, source, class_year, player_rank, player_grade, stars, link, position, height, weight, school_name, city, state, location_type, is_finalized)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_player_sql = "INSERT INTO players (full_name, class_year, current_level) VALUES (%s, %s, %s)"

# ----------------------------
# 🔧 Process scraped data
# ----------------------------

for data_set in (data_247, data_espn, data_rivals):
    for record in data_set:
        (source, class_year, player_rank, grade, stars, player_name,
        player_link, position, height, weight,
        school_name, city, state, location_type, finalized) = record

        # Try fuzzy match first
        player_uid = find_matching_player(cursor, class_year, player_name)

        if not player_uid:
            # No match found, insert new player
            cursor.execute(insert_player_sql, (player_name, class_year, 'HS'))
            player_uid = cursor.lastrowid

        # Insert ranking record
        cursor.execute(insert_rank_sql, (
            player_uid, source, class_year, player_rank, grade, stars,
            player_link, position, height, weight,
            school_name, city, state, location_type, finalized
        ))

cnx.commit()
cursor.close()
cnx.close()

print("✅ Data inserted successfully!")