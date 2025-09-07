from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_LINEUP_BUILDER, nba_lineup_content
from fastapi import HTTPException

import json

client = set_gemini_key()

async def create_nba_lineup_analysis(mode: str, player_info: list) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_LINEUP_BUILDER},
        {"role": "user", "content": nba_lineup_content(mode, player_info)}
    ]

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
        )

        # AI raw output
        analysis_str = response.choices[0].message.content.strip()
        print("RAW AI OUTPUT:", analysis_str)

        # 🔑 Remove code fences if present
        if analysis_str.startswith("```"):
            analysis_str = analysis_str.strip("`")  # drop all backticks
            if analysis_str.lower().startswith("json"):
                analysis_str = analysis_str[4:].strip()  # drop "json" language hint

        # Parse JSON
        try:
            analysis_json = json.loads(analysis_str)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis did not return valid JSON: {str(e)} | OUTPUT: {analysis_str}"
            )

        # Validate keys
        required_keys = [
            "overallScore", "strengths", "weaknesses",
            "synergyNotes", "floor", "ceiling", "overallAnalysis"
        ]
        if not all(key in analysis_json for key in required_keys):
            raise HTTPException(
                status_code=500,
                detail=f"AI JSON is missing required keys | OUTPUT: {analysis_json}"
            )

        return analysis_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")
