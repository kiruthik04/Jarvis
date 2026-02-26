import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
    
    # Browser config could go here
    HEADLESS_BROWSER = False

    # Set GMAIL_ENABLED=false in .env to skip Google auth on startup
    GMAIL_ENABLED = os.getenv("GMAIL_ENABLED", "true").lower() == "true"
