from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_MATCHUP_SIMULATION, matchup_simulation_content
from fastapi import HTTPException

import json

client = set_gemini_key()

async def create_matchup_simulation_analysis(lineup1, lineup2) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_MATCHUP_SIMULATION},
        {"role": "user", "content": matchup_simulation_content(lineup1, lineup2)}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
        )

        analysis_str = response.choices[0].message.content.strip()

        if analysis_str.startswith("```"):
            analysis_str = analysis_str.strip("`")
            if analysis_str.lower().startswith("json"):
                analysis_str = analysis_str[4:].strip()

        try:
            analysis_json = json.loads(analysis_str)
        except json.JSONDecodeError as e:
            print("Gemini API error:", str(e))
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis did not return valid JSON: {str(e)} | OUTPUT: {analysis_str}"
            )

        # Validate keys
        required_keys = [
            "scoreA", "scoreB", "mvp",
            "keyStats", "players", "reasoning"
        ]
        if not all(key in analysis_json for key in required_keys):
            raise HTTPException(
                status_code=500,
                detail=f"AI JSON is missing required keys | OUTPUT: {analysis_json}"
            )

        return analysis_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")