from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_HOT_TAKE, hot_take_content
from fastapi import HTTPException

import json

client = set_gemini_key()

async def create_hot_take_analysis(content: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_HOT_TAKE},
        {"role": "user", "content": hot_take_content(content)}
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
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis did not return valid JSON: {str(e)} | OUTPUT: {analysis_str}"
            )

        required_keys = ["truthfulness_score", "ai_insight"]
        
        if not all(key in analysis_json for key in required_keys):
            raise HTTPException(
                status_code=500,
                detail=f"AI JSON is missing required keys | OUTPUT: {analysis_json}"
            )

        return analysis_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")