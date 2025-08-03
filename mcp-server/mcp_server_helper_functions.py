import mysql.connector
import os

from dotenv import load_dotenv

dotenv_path = '.env'

# Load the .env file
load_dotenv(dotenv_path)

# Access environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

cnx = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database='swish_report'
)
cursor = cnx.cursor()

def fetch_player_rankings(player_name, class_year):
    get_player_uid_query = """
    SELECT player_uid FROM players WHERE full_name = %s AND class_year = %s
    """
    cursor.execute(get_player_uid_query, (player_name, class_year))
    result = cursor.fetchone()

    if not result:
        print(f"❌ No player found with name '{player_name}' and class_year '{class_year}'")
        cursor.close()
        cnx.close()
        return []

    player_uid = result['player_uid']

    # Step 2: Get rankings for that player
    get_rankings_query = """
    SELECT * FROM high_school_player_rankings WHERE player_uid = %s
    """
    cursor.execute(get_rankings_query, (player_uid,))
    rankings = cursor.fetchall()

    cursor.close()
    cnx.close()

    return rankings