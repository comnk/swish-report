from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from random import randint
from typing import Dict, Union, Literal

from core.db import get_db_connection
from scripts.insertion.ai_generation.insert_nba_lineup_analysis import create_nba_lineup_analysis
from scripts.insertion.ai_generation.insert_hot_take_analysis import create_hot_take_analysis
from scripts.insertion.ai_generation.insert_player_comparison_analysis import create_player_comparison_analysis
from scripts.insertion.ai_generation.insert_matchup_simulation_analysis import create_matchup_simulation_analysis
from utils.nba_helpers import fetch_nba_player_stats, handle_name, normalize_season

import json

router = APIRouter()

class LineupSubmission(BaseModel):
    mode: Literal["starting5", "rotation"]
    lineup: Dict[str, Union[str, None]]  # positions mapped to player names or null
    email: str

class MatchupSimulationSubmission(BaseModel):
    lineup1: Dict[str, Union[str, None]]
    lineup2: Dict[str, Union[str, None]]

class HotTakeSubmission(BaseModel):
    user_id: str
    content: str

class PlayerComparisonSubmission(BaseModel):
    player1_id: str
    player2_id: str

@router.get("/poeltl/get-player")
def poeltl_get_daily_player():
    select_sql = """
    SELECT p.full_name, nba.position, nba.height, nba.weight, nba.years_pro, nba.teams, nba.accolades FROM players AS p INNER JOIN nba_player_info AS nba ON p.player_uid=nba.player_uid WHERE current_level='NBA';
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql)
    
    rows = cursor.fetchall()
    
    random_index = randint(0, len(rows) - 1)
    random_player = rows[random_index]
    print(random_player)
    return random_player


@router.post("/player-comparison/get-comparison")
async def get_player_comparison(submission: PlayerComparisonSubmission):
    select_sql = "SELECT * FROM nba_player_stats WHERE player_uid=%s ORDER BY stat_id ASC;"
    insert_sql = """
        INSERT INTO nba_player_stats (
            player_uid, season, team, gp, ppg, apg, rpg, spg, bpg, topg,
            fpg, pts, fga, fgm, three_pa, three_pm, fta, ftm,
            ts_pct, fg, efg, three_p, ft
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    get_name_sql = "SELECT full_name FROM players WHERE player_uid=%s;"

    def get_or_fetch_player(pid: int, cursor, conn) -> dict:
        # 1️⃣ Try to read from DB
        cursor.execute(select_sql, (pid,))
        stats_rows = cursor.fetchall()

        cursor.execute(get_name_sql, (pid,))
        row = cursor.fetchone()
        full_name = handle_name(row["full_name"]) if row and row.get("full_name") else f"Unknown Player {pid}"

        if stats_rows:
            normalized = [normalize_season(r) for r in stats_rows]
            return {"player_uid": pid, "full_name": full_name, "seasons": normalized}

        # 2️⃣ Fetch from NBA API if not in DB
        season_stats = fetch_nba_player_stats(full_name) or []
        if not season_stats:
            raise HTTPException(status_code=500, detail=f"No stats found for {full_name}")

        all_stats = []
        for season in season_stats:
            normalized = normalize_season(season)
            values = (
                pid,
                normalized["season"],
                normalized["team"],
                normalized["gp"],
                normalized["ppg"],
                normalized["apg"],
                normalized["rpg"],
                normalized["spg"],
                normalized["bpg"],
                normalized["topg"],
                normalized["fpg"],
                normalized["pts"],
                normalized["fga"],
                normalized["fgm"],
                normalized["three_pa"],
                normalized["three_pm"],
                normalized["fta"],
                normalized["ftm"],
                normalized["ts_pct"],
                normalized["fg"],
                normalized["efg"],
                normalized["three_p"],
                normalized["ft"],
            )
            cursor.execute(insert_sql, values)
            all_stats.append(normalized)

        conn.commit()
        return {"player_uid": pid, "full_name": full_name, "seasons": all_stats}

    # 3️⃣ Fetch both players
    players_data = {}
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            for pid in [submission.player1_id, submission.player2_id]:
                players_data[pid] = get_or_fetch_player(pid, cursor, conn)
        finally:
            cursor.close()
    finally:
        conn.close()

    # 4️⃣ Get latest stats
    def get_latest_stats(player: dict):
        seasons = player.get("seasons", [])
        if not seasons:
            return {"ppg": 0, "apg": 0, "rpg": 0}
        latest = seasons[-1]
        return {
            "ppg": latest.get("ppg", 0),
            "apg": latest.get("apg", 0),
            "rpg": latest.get("rpg", 0),
        }

    # 5️⃣ AI analysis
    ai_analysis = await create_player_comparison_analysis(
        players_data[submission.player1_id],
        players_data[submission.player2_id]
    )

    result = {
        "player1": {
            "full_name": players_data[submission.player1_id]["full_name"],
            "latest": get_latest_stats(players_data[submission.player1_id]),
            "all_seasons": players_data[submission.player1_id]["seasons"],
        },
        "player2": {
            "full_name": players_data[submission.player2_id]["full_name"],
            "latest": get_latest_stats(players_data[submission.player2_id]),
            "all_seasons": players_data[submission.player2_id]["seasons"],
        },
        "ai_analysis": ai_analysis
    }

    return JSONResponse(content=jsonable_encoder(result))


@router.post("/lineup-builder/submit-lineup", response_model=dict)
async def get_lineup_analysis(submission: LineupSubmission):
    """
    Takes a lineup submission, generates AI analysis, and inserts into the DB.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (submission.email,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row["user_id"]

        player_ids = list(submission.lineup.values())
        placeholders = ",".join(["%s"] * len(player_ids))

        select_sql = f"""
            SELECT
                p.player_uid,
                p.full_name,
                nba.position,
                nba.height,
                nba.weight,
                nba.years_pro,
                nba.accolades,
                ai.stars,
                ai.rating,
                ai.strengths,
                ai.weaknesses,
                ai.ai_analysis
            FROM players AS p
            INNER JOIN nba_player_info AS nba
                ON p.player_uid = nba.player_uid
            INNER JOIN ai_generated_nba_evaluations AS ai
                ON p.player_uid = ai.player_uid
            WHERE p.player_uid IN ({placeholders})
        """
        cursor.execute(select_sql, player_ids)
        results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No players found for lineup")

        analysis_json = await create_nba_lineup_analysis(submission.mode, results)
        print(analysis_json)

        insert_sql = """
            INSERT INTO lineups (user_id, mode, players, scouting_report)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_sql,
            (
                user_id,
                submission.mode,
                json.dumps(submission.lineup),
                json.dumps(analysis_json),
            ),
        )
        conn.commit()
        lineup_id = cursor.lastrowid

        return {
            "message": "Lineup submitted successfully",
            "lineup_id": lineup_id,
            "scouting_report": analysis_json,
            "players": results,
        }

    finally:
        cursor.close()
        conn.close()

@router.post("/hot_take")
async def submit_hot_take(submission: HotTakeSubmission):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (submission.user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row["user_id"]

        analysis_json = await create_hot_take_analysis(submission.content)

        insert_sql = """
            INSERT INTO hot_takes (user_id, content, truthfulness_score, ai_insight)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_sql,
            (
                user_id,
                submission.content,
                analysis_json["truthfulness_score"],
                analysis_json["ai_insight"],
            ),
        )
        conn.commit()
        take_id = cursor.lastrowid

        return {
            "message": "Hot take submitted successfully",
            "take_id": take_id,
            "hot_take_analysis": analysis_json,
        }

    finally:
        cursor.close()
        conn.close()


@router.post("/simulated-matchups/submit-matchup", response_model=dict)
async def simulated_matchups(submission: MatchupSimulationSubmission):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        player_ids = list(submission.lineup1.values()) + list(submission.lineup2.values())
        placeholders = ",".join(["%s"] * len(player_ids))

        select_sql = f"""
            SELECT
                p.player_uid,
                p.full_name,
                nba.position,
                nba.height,
                nba.weight,
                nba.years_pro,
                nba.accolades,
                ai.stars,
                ai.rating,
                ai.strengths,
                ai.weaknesses,
                ai.ai_analysis
            FROM players AS p
            INNER JOIN nba_player_info AS nba
                ON p.player_uid = nba.player_uid
            INNER JOIN ai_generated_nba_evaluations AS ai
                ON p.player_uid = ai.player_uid
            WHERE p.player_uid IN ({placeholders})
        """
        cursor.execute(select_sql, player_ids)
        results = cursor.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No players found for lineup")

        player_lookup = {str(row["player_uid"]): row for row in results}

        lineup1 = {slot: player_lookup.get(pid) for slot, pid in submission.lineup1.items()}
        lineup2 = {slot: player_lookup.get(pid) for slot, pid in submission.lineup2.items()}

        analysis_json = await create_matchup_simulation_analysis(lineup1, lineup2)
        print(analysis_json)
        
        return {
            "scoreA": analysis_json["scoreA"],
            "scoreB": analysis_json["scoreB"],
            "mvp": analysis_json["mvp"],
            "keyStats": analysis_json["keyStats"],
            "players": analysis_json["players"],
            "reasoning": analysis_json["reasoning"],
        }

    finally:
        cursor.close()
        conn.close()

