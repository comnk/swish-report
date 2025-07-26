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

print(DB_USER, DB_PASSWORD, DB_HOST)

# Connect without a database first to create one
cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = cnx.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS swish_report")
cnx.close()

# Now connect to that database
cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='swish_report')
cursor = cnx.cursor()

# Create table with proper schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS player_rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    class_year VARCHAR(10),
    player_rank INT,
    name VARCHAR(255) NOT NULL,
    link TEXT,
    position VARCHAR(50),
    height VARCHAR(20),
    weight VARCHAR(20),
    school_name VARCHAR(255),
    school_city VARCHAR(100),
    school_state VARCHAR(50),
    location_type VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")

# cursor.execute("""
# CREATE TABLE player_analysis (
#     analysis_id INT AUTO_INCREMENT PRIMARY KEY,
#     player_id INT,
#     source ENUM('nbadraftnet','nbadraftroom'),
#     heading TEXT,
#     paragraph LONGTEXT,
#     scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (player_id) REFERENCES players(player_id)
# );
# """)

print("Database and table created successfully!")
cnx.close()