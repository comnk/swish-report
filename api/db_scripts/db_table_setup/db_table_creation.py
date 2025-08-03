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
CREATE TABLE IF NOT EXISTS players (
    player_uid INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    class_year INT NULL,
    current_level ENUM('HS','COLLEGE','NBA', 'NONE') NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")

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
CREATE TABLE IF NOT EXISTS high_school_player_rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    source VARCHAR(50) NOT NULL,
    class_year VARCHAR(10),
    player_rank INT DEFAULT NULL,
    player_grade INT,
    stars INT,
    link TEXT,
    position VARCHAR(50),
    height VARCHAR(20),
    weight VARCHAR(20),
    school_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    location_type VARCHAR(50),
    is_finalized BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS high_school_player_ranking_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    snapshot_date DATE NOT NULL,
    source ENUM('247sports') NOT NULL,
    player_rank INT DEFAULT NULL,
    player_rating INT,
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS high_school_player_evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    evaluator_name VARCHAR(255),
    evaluation_date DATE,
    notes MEDIUMTEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES high_school_player_rankings(id)
);
""")

print("Database and tables created successfully!")
cnx.close()