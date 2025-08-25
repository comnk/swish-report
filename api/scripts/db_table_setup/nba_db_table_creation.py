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

# DRAFT EVALS: consistent FK name + InnoDB
cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_draft_evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    source VARCHAR(255) NOT NULL,
    notes MEDIUMTEXT NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_nde_player FOREIGN KEY (player_uid)
        REFERENCES players(player_uid) ON DELETE CASCADE
) ENGINE=InnoDB;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_player_info (
    info_uid INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    player_url VARCHAR(255),
    position VARCHAR(50),
    height VARCHAR(20),
    weight VARCHAR(20),
    teams JSON,
    min_year INT,
    max_year INT,
    draft_round INT,
    draft_pick INT,
    draft_year INT,
    years_pro INT,
    accolades JSON,
    colleges JSON,
    high_schools JSON,
    is_active BOOLEAN,
    data_hash VARCHAR(32),
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_player_year (player_uid, draft_year),
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
) ENGINE=InnoDB;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_teams ()
""")

# PLAYER STATS: remove duplicate player_id, add PK, unique (player_uid, season_id), InnoDB
cursor.execute("""
CREATE TABLE IF NOT EXISTS nba_player_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    season_id VARCHAR(10) NOT NULL,
    team_id INT,
    team_abbreviation VARCHAR(10),
    gp INT,
    pts FLOAT,
    reb FLOAT,
    ast FLOAT,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_player_season (player_uid, season_id),
    CONSTRAINT fk_nps_player FOREIGN KEY (player_uid)
        REFERENCES players(player_uid) ON DELETE CASCADE
) ENGINE=InnoDB;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_generated_nba_evaluations (
    ai_evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    stars INT NOT NULL,
    rating INT NOT NULL,
    strengths JSON NOT NULL,
    weaknesses JSON NOT NULL,
    ai_analysis MEDIUMTEXT NOT NULL,
    CONSTRAINT uq_player_uid UNIQUE (player_uid),
    CONSTRAINT fk_ai_player_uid FOREIGN KEY (player_uid) REFERENCES players(player_uid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

print("Database and tables created successfully!")
cnx.close()