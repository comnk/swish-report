CREATE TABLE lineups (
    lineup_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    mode ENUM('starting5', 'rotation10') NOT NULL,
    players JSON NOT NULL,
    scouting_report JSON NOT NULL,
    overall_score TINYINT UNSIGNED GENERATED ALWAYS AS (
        JSON_UNQUOTE(
            JSON_EXTRACT(
                scouting_report,
                '$.overallScore'
            )
        )
    ) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_lineups_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);