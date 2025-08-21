from api.core.db import get_db_connection

def insert_hs_player(full_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    insert_rank_sql = """
    INSERT INTO high_school_player_rankings
    (player_uid, source, class_year, player_rank, player_grade, stars, link, position, height, weight,
    school_name, city, state, location_type, is_finalized)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        player_rank   = VALUES(player_rank),
        player_grade  = VALUES(player_grade),
        stars         = VALUES(stars),
        link          = VALUES(link),
        position      = VALUES(position),
        height        = VALUES(height),
        weight        = VALUES(weight),
        school_name   = VALUES(school_name),
        city          = VALUES(city),
        state         = VALUES(state),
        location_type = VALUES(location_type),
        is_finalized  = VALUES(is_finalized),
        last_updated  = CURRENT_TIMESTAMP;
    """

    insert_player_sql = """
    INSERT INTO players (full_name, class_year, current_level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE current_level = VALUES(current_level), class_year = VALUES(class_year);
    """
    
    cursor.execute(insert_player_sql, (full_name,))