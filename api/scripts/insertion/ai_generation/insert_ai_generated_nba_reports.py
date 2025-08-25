from api.core.config import set_gemini_key

client = set_gemini_key()

insert_sql = """
INSERT INTO ai_generated_nba_evaluations
    (player_uid, stars, rating, strengths, weaknesses, ai_analysis)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    stars = VALUES(stars),
    rating = VALUES(rating),
    strengths = VALUES(strengths),
    weaknesses = VALUES(weaknesses),
    ai_analysis = VALUES(ai_analysis);
"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain to me how AI works"
        }
    ]
)

print(response.choices[0].message.content)

select_sql = """
SELECT p.player_uid, p.full_name
"""

def main():
    pass

if __name__ == "__main__":
    main()