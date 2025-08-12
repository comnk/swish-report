from api.core.db import get_db_connection

cnx = get_db_connection()
cursor = cnx.cursor()

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