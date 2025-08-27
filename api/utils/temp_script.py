from nba_api.stats.static import players
from core.db import get_db_connection
from unidecode import unidecode
from rapidfuzz import process, fuzz

def normalize_name(name):
    return unidecode(name).lower().strip()

# Connect to DB
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

# Fetch all DB players
cursor.execute("SELECT full_name, player_uid FROM players WHERE current_level='NBA'")
db_players = cursor.fetchall()

# Fetch all NBA API players
all_players = players.get_players()
nba_api_names = [p['full_name'] for p in all_players]

# Normalize NBA API names for matching
nba_api_names_norm = [normalize_name(name) for name in nba_api_names]

# Check DB players
potential_missing = []

for row in db_players:
    db_name_norm = normalize_name(row['full_name'])
    match, score, _ = process.extractOne(db_name_norm, nba_api_names_norm, scorer=fuzz.ratio)
    
    # If match is very low, consider it missing
    if score < 80:
        potential_missing.append(row['full_name'])

print("Players potentially missing from NBA API (manual review required):")
for name in potential_missing:
    print("-", name)

cursor.close()
conn.close()

# from nba_api.stats.static import players
# from nba_api.stats.endpoints import playercareerstats

# # Find the player by name
# player_info = players.find_players_by_full_name("Jimmy Butler")
# if player_info:
#     player_id = player_info[0]['id']  # Get the first matching player's ID
    
#     # Fetch career stats
#     career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
#     stats_df = career_stats.get_data_frames()[0]  # Pandas DataFrame with stats
    
#     print(stats_df.head())  # Display first few rows
# else:
#     print("Player not found in NBA API.")