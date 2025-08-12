from openai import OpenAI

import os

def set_openai():
    OPENAI_KEY = os.getenv('OPENAI_KEY')
    if not OPENAI_KEY:
        raise ValueError("OPENAI_KEY not found")
    
    client = OpenAI(api_key=OPENAI_KEY)
    return client