CREATE TABLE lineups (
    lineup_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, -- FK to users table
    mode ENUM('starting5', 'rotation10') NOT NULL,
    players JSON NOT NULL, -- array of player_ids or names
    scouting_report JSON NOT NULL, -- full LLM report JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);