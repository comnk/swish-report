from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_PLAYER_COMPARISON, player_comparison_content
from fastapi import HTTPException

client = set_gemini_key()

async def create_player_comparison_analysis(player1_data, player2_data):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_PLAYER_COMPARISON},
        {"role": "user", "content": player_comparison_content(player1_data, player2_data)}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
        )

        analysis_str = response.choices[0].message.content.strip()
        return analysis_str

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")