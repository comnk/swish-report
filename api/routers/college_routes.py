from fastapi import APIRouter, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel

from core.db import get_db_connection

router = APIRouter()

CACHE_EXPIRY_HOURS = 6

class PlayerSubmission(BaseModel):
    name: str
    basketball_reference_link: Optional[str] = None

@router.get("/prospects", response_model=List[dict])
def get_college_prospects():
    cnx = get_db_connection()
    cursor = cnx.cursor()

@router.get("/prospects/{player_id}")
def get_college_player(player_id: int):
    pass

@router.get("/prospects/{player_id}/videos")
def get_nba_player_videos(player_id: int, background_tasks: BackgroundTasks):
    pass

def refresh_player_videos(player_id: int, full_name: str, class_year: int):
    pass

@router.post("/players/submit-player", response_model=Dict)
async def submit_high_school_player(submission: PlayerSubmission):
    pass