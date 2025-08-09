from fastapi import APIRouter
from typing import List
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from pydantic import BaseModel
from dotenv import load_dotenv

import mysql.connector

router = APIRouter()

@router.get("/players", response_model=List[dict])
def get_nba_prospects(page: int = 1, limit: int = 12):
    nba_players = players.get_active_players()
    start = (page - 1) * limit
    end = start + limit
    selected_players = nba_players[start:end]
    print("HEEEEEEE")

    player_data = []
    for p in selected_players:
        player_id = p["id"]
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        info_data = info.get_normalized_dict()["CommonPlayerInfo"][0]
        player_data.append({
            "id": player_id,
            "full_name": p["full_name"],
            "position": info_data.get("POSITION"),
            "height": info_data.get("HEIGHT")
        })
    
    print(player_data)

    return player_data