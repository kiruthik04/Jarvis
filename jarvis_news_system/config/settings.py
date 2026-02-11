import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "chroma_db"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# ChromaDB Settings
CHROMA_PERSIST_DIRECTORY = str(DB_DIR)
COLLECTION_NAME = "jarvis_news_knowledge"

# Embedding Model
# "all-MiniLM-L6-v2" is a fast, high-quality model for English text
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

# RSS Feeds Configuration
RSS_FEEDS = {
    "tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://news.ycombinator.com/rss",
        "https://arstechnica.com/feed/"
    ],
    "science": [
        "https://www.sciencedaily.com/rss/top/science.xml",
        "https://www.wired.com/feed/category/science/latest/rss"
    ],
    "world": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ],
    "finance": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html"
    ]
}

# Scheduler Settings
# Time in 24h format
UPDATE_TIME = "06:00" 

# System Settings
MAX_ARTICLES_PER_FEED = 5
SIMILARITY_THRESHOLD = 0.7
TOP_K_RETRIEVAL = 3
