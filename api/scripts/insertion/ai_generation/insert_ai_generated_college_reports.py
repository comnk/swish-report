from core.db import get_db_connection
from core.config import set_gemini_key

client = set_gemini_key()

def get_scouting_report_with_retry(player_uid, player_name, retries=3):
    pass