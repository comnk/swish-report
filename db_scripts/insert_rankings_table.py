import mysql.connector
import os
from dotenv import load_dotenv
from fetch_rankings_script import fetch_247_sports_info, fetch_espn_info, fetch_rivals_info

dotenv_path = '../../.env'
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

rankings_247 = fetch_247_sports_info(2027)
print("Successfully loaded 247 rankings")
espn_rankings = fetch_espn_info(2027)
print("Successfully loaded ESPN rankings")
rivals_rankings = fetch_rivals_info(2027)
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
(source, class_year, player_rank, name, link, position, height, weight, school_name, school_city, school_state, location_type)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def prepare_data(records, source_name, class_year):
    """
    Convert a list of dicts like:
    {'rank': '111', 'name': 'Joshua Rivera', 'link': '...', 'position': 'SF', 'height': '6-7', 'weight': '165'}
    into tuples matching insert_sql order.
    """
    prepared = []
    for rec in records:
        prepared.append((
            source_name,
            str(class_year),
            rec.get('player_rank'),
            rec.get('name'),
            rec.get('link'),
            rec.get('position'),
            rec.get('height'),
            rec.get('weight'),
            rec.get('school_name'),
            rec.get('school_city'),
            rec.get('school_state'),
            rec.get('location_type')
        ))
    return prepared

# Prepare each dataset
data_247 = prepare_data(rankings_247, '247sports', 2027)
data_espn = prepare_data(espn_rankings, 'espn', 2027)
data_rivals = prepare_data(rivals_rankings, 'rivals', 2027)

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