from fastapi import APIRouter
from typing import List
from fastapi import HTTPException
import mysql.connector
from typing import List

import os
import json
from dotenv import load_dotenv

router = APIRouter()

def get_db_connection():
    dotenv_path = '.env'
    load_dotenv(dotenv_path)

    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database='swish_report'
    )

@router.get("/prospects", response_model=List[dict])
def get_highschool_prospects():
    select_sql = """
    SELECT
        p.player_uid,
        p.full_name,
        p.class_year,
        hspr.position,
        hspr.school_name,
        hspr.height,
        COALESCE(ai.stars, 4) AS stars,
        COALESCE(ai.rating, 85) AS overallRating,
        COALESCE(ai.strengths, JSON_ARRAY('Scoring', 'Athleticism', 'Court Vision')) AS strengths,
        COALESCE(ai.weaknesses, JSON_ARRAY('Defense', 'Consistency')) AS weaknesses,
        COALESCE(ai.ai_analysis, 'A highly talented high school prospect with excellent scoring ability and strong athletic traits.') AS aiAnalysis
    FROM players AS p
    INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
    LEFT JOIN ai_generated_high_school_evaluations AS ai ON ai.player_id = p.player_uid
    WHERE hspr.source = '247sports' AND p.current_level="HS";
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Parse JSON strings for strengths and weaknesses to Python lists
        for row in rows:
            # If strengths is a string (JSON), parse it, else use default list
            if isinstance(row['strengths'], str):
                try:
                    row['strengths'] = json.loads(row['strengths'])
                except json.JSONDecodeError:
                    row['strengths'] = ["Scoring", "Athleticism", "Court Vision"]
            if isinstance(row['weaknesses'], str):
                try:
                    row['weaknesses'] = json.loads(row['weaknesses'])
                except json.JSONDecodeError:
                    row['weaknesses'] = ["Defense", "Consistency"]

        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))