from core.db import get_db_connection

# Now connect to that database
cnx = get_db_connection()
cursor = cnx.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS college_player_info (
    info_uid INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    player_url VARCHAR(255),         -- Sports Reference player page
    position VARCHAR(50),            -- e.g. "G", "F", "C"
    height VARCHAR(10),              -- e.g. "6-5"
    weight INT,                      -- in pounds
    years VARCHAR(20),               -- e.g. "(2011-2015)"
    schools JSON,                    -- list of schools (name + url)
    is_active BOOLEAN DEFAULT TRUE,  -- optional flag
    data_hash VARCHAR(32),           -- hash for deduping
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_player_year (player_uid, years),
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
) ENGINE=InnoDB;
""")