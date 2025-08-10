from nba_api.stats.static import players
from dotenv import load_dotenv

import os
import mysql.connector

# Get NBA players
nba_players = players.get_players()

dotenv_path = '../../.env'
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

# Connect to MySQL
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database='swish_report',
    autocommit=True
)
cursor = conn.cursor()

# Insert NBA players into the master players table
insert_sql = """
INSERT INTO players (full_name, class_year, current_level)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    current_level = VALUES(current_level)
"""

for p in nba_players:
    # p looks like:
    # {'id': 1505, 'full_name': 'Tariq Abdul-Wahad', 'first_name': 'Tariq', 'last_name': 'Abdul-Wahad', 'is_active': False}
    
    # class_year is unknown for NBA players — keep it NULL
    cursor.execute(insert_sql, (p["full_name"], None, "NBA"))

# Commit changes
conn.commit()
cursor.close()
conn.close()
