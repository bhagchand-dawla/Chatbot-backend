import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

claude_key = os.getenv("CLAUDE_KEY")
claude_client = anthropic.Client(api_key=claude_key)

def llmNameGenerate(query):
    response = claude_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2048,
        system="You are a language model designed to analyze conversations and generate descriptive names for chat threads.",
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        top_p=1,
        )
    return response.content[0].text


query = "Tell me about yourself"

response = llmNameGenerate(query)

print(response)