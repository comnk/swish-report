from core.db import get_db_connection
from core.config import set_openai

client = set_openai()

def get_scouting_report_with_retry(player_uid, player_name, retries=3):
    pass