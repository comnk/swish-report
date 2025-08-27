from core.db import get_db_connection

# Now connect to that database
cnx = get_db_connection()
cursor = cnx.cursor()

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
    player_image TEXT,
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
CREATE TABLE IF NOT EXISTS ai_generated_high_school_evaluations (
    ai_evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    stars INT NOT NULL,
    rating INT NOT NULL,
    strengths JSON NOT NULL,
    weaknesses JSON NOT NULL,
    ai_analysis MEDIUMTEXT NOT NULL,
    CONSTRAINT uq_player_uid UNIQUE (player_uid),
    CONSTRAINT fk_player_uid FOREIGN KEY (player_uid) REFERENCES players(player_uid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

print("Database and tables created successfully!")
cnx.close()