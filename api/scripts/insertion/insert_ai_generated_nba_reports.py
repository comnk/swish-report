from api.core.config import set_gemini_key

client = set_gemini_key()

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