import mysql.connector
import os

from dotenv import load_dotenv

dotenv_path = '../../.env'

# Load the .env file
load_dotenv(dotenv_path)

# Access environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

# Connect without a database first to create one
cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = cnx.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS swish_report")
cnx.close()

# Now connect to that database
cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='swish_report')
cursor = cnx.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_draft_evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    source VARCHAR(255) NOT NULL,
    notes MEDIUMTEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_uid)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_player_info (
    player_uid INT PRIMARY KEY,
    team VARCHAR(100) NULL,
    position VARCHAR(50) NULL,
    height VARCHAR(10) NULL,
    weight INT NULL,
    jersey_number INT NULL,
    draft_year INT NULL,
    draft_round INT NULL,
    draft_pick INT NULL,
    years_pro INT NULL,
    college VARCHAR(255) NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (player_uid) REFERENCES players(player_uid) ON DELETE CASCADE
);
""")

print("Database and tables created successfully!")
cnx.close()