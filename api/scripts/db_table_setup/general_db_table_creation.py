from api.core.db import get_db_connection

cnx = get_db_connection()
cursor = cnx.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS swish_report")
cnx.close()

cursor.execute("""
CREATE TABLE players (
    player_uid INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    current_level ENUM('HS','COLLEGE','INTERNATIONAL','G-LEAGUE','NBA') NULL DEFAULT 'NBA',
    class_year INT NULL,
    draft_year INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_level_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    level ENUM('HS', 'COLLEGE', 'NBA', 'NONE') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    level ENUM('high_school_247', 'high_school_rivals', 'college', 'nba', 'gleague', 'international') NOT NULL,
    image_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (player_uid)
        REFERENCES players (player_uid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")