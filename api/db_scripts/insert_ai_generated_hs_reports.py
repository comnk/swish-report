import os
import time

from openai import OpenAI
from dotenv import load_dotenv

dotenv_path = '../.env'
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
OPENAI_KEY = os.getenv('OPENAI_KEY')

client = OpenAI(api_key=OPENAI_KEY)

players = [
    "Darius Acuff Jr.",
    "Meleek Thomas",
    "Beckham Black"
]

system_prompt = """
You are a basketball recruiting expert that scouts high school, college, and NBA talent.

When the user asks for a scouting report, you must return a JSON object in this format:

{
    rating: [rating of player from 50 to 100] (do not be lenient on these ratings),
    strengths: [list of strengths the player has that can be used as tags on the frontend],
    weaknesses: [list of weaknesses the player has that can be used as tags on the frontend],
    aiAnalysis: [your analysis of that specific player]
}
"""

def get_scouting_report(player_name: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"give a scouting report on {player_name}."}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=messages
    )
    return response.choices[0].message.content

reports = {}
for player in players:
    try:
        report = get_scouting_report(player)
        reports[player] = report
        print(f"Got report for {player}")
    except Exception as e:
        print(f"Error for {player}: {e}")
    
    time.sleep(1)  # pause 1 second between calls to avoid rate limit

# Now `reports` contains JSON strings with scouting reports per player.