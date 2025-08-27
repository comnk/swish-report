from core.db import get_db_connection

# Now connect to that database
cnx = get_db_connection()
cursor = cnx.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS college_player_info (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    profile_url VARCHAR(255) NOT NULL UNIQUE,
    start_year INT NULL,
    end_year INT NULL,
    schools VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")