from api.core.db import get_db_connection

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
CREATE TABLE IF NOT EXISTS ai_generated_high_school_evaluations (
    ai_evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL UNIQUE,
    stars INT NOT NULL,
    rating INT NOT NULL,
    strengths JSON NOT NULL,
    weaknesses JSON NOT NULL,
    ai_analysis MEDIUMTEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS 247_high_school_player_evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    evaluator_name VARCHAR(255),
    evaluation_date DATE,
    notes MEDIUMTEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES high_school_player_rankings(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hs_social_media_content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_uid INT NOT NULL,
    platform ENUM('YOUTUBE', 'TWITTER') NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    url TEXT NOT NULL,
    thumbnail_url TEXT,
    author VARCHAR(255),
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_uid) REFERENCES players(player_uid)
);
""")

print("Database and tables created successfully!")
cnx.close()