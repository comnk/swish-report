from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_PLAYER_COMPARISON
from fastapi import HTTPException

client = set_gemini_key()

from decimal import Decimal
import json


async def create_player_comparison_analysis(player1: dict, player2: dict):
    def safe(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, dict):
            return {k: safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [safe(v) for v in obj]
        return obj

    player1_safe = safe(player1)
    player2_safe = safe(player2)

    user_content = f"""
Compare these two players:

{player1_safe['full_name']} - Seasons: {json.dumps(player1_safe['seasons'], ensure_ascii=False)}

{player2_safe['full_name']} - Seasons: {json.dumps(player2_safe['seasons'], ensure_ascii=False)}
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_PLAYER_COMPARISON},
        {"role": "user", "content": user_content}
    ]

    try:
        response = client.chat.completions.create(  # no await
            model="gemini-2.5-pro",
            messages=messages,
        )

        analysis_str = response.choices[0].message.content.strip()  # like lineup version
        print("Analysis Str: ", analysis_str)
        return analysis_str

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")
