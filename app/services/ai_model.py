import openai
import os
from fastapi import HTTPException

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_answer(query: str):
    """Fetches an AI-generated answer using OpenAI GPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": query}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
