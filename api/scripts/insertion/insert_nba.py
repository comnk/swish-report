from api.core.db import get_db_connection
cnx = get_db_connection()
cursor = cnx.cursor()

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def insert_nba_players():
    # Insert NBA players into the master players table
    insert_sql = """
    INSERT INTO players (full_name, class_year, current_level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        full_name = VALUES(full_name),
        current_level = VALUES(current_level)
    """

def insert_nba_player_details():
    cursor.execute("""SELECT full_name FROM players WHERE current_level = "NBA" """)

    cursor.close()
    cnx.close()


def main():
    result = insert_nba_player_details()
    print(result)

main()