from api.core.db import get_db_connection

cnx = get_db_connection()
cursor = cnx.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_uid INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    class_year INT NOT NULL,
    current_level VARCHAR(50) NOT NULL DEFAULT 'NBA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_fullname_classyear (full_name, class_year)
) ENGINE=InnoDB;
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