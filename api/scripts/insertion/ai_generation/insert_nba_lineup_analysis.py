from core.config import set_gemini_key
from utils.ai_prompts import SYSTEM_PROMPT_LINEUP_BUILDER, nba_lineup_content

client = set_gemini_key()

async def create_nba_lineup_analysis(mode, player_info):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_LINEUP_BUILDER},
        {"role": "user", "content": nba_lineup_content(mode, player_info)}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        err_str = str(e).lower()
        raise err_str