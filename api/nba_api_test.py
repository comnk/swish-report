from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.endpoints import drafthistory

draft_df = drafthistory.DraftHistory()
draft_df.get_json()

# get_players returns a list of dictionaries, each representing a player.
nba_players = players.get_players()
print(nba_players[:5])

big_fundamental = [
    player for player in nba_players if player["full_name"] == "Tim Duncan"
][0]
big_fundamental

draft = drafthistory.DraftHistory(season_year_nullable='2023') 
draft_data = draft.get_data_frames()[0]
# print(draft_data)