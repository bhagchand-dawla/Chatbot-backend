import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

config = Config()
