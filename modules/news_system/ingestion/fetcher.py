import feedparser
import logging
from typing import List, Dict, Any
from jarvis_news_system.config import settings

logger = logging.getLogger(__name__)

class NewsFetcher:
    """
    Fetches news from configured RSS feeds.
    """
    def __init__(self):
        self.feeds = settings.RSS_FEEDS

    def fetch_all_news(self) -> List[Dict[str, Any]]:
        """
        Iterates through all configured feeds and fetches articles.
        Returns a list of raw article dictionaries.
        """
        all_articles = []
        logger.info("Starting news fetch...")
        
        for category, urls in self.feeds.items():
            for url in urls:
                try:
                    logger.info(f"Fetching {category} news from: {url}")
                    feed = feedparser.parse(url)
                    
                    if feed.bozo:
                        logger.warning(f"Feed {url} has parsing errors: {feed.bozo_exception}")
                        # Depending on severity, we might still get entries, so continuing

                    # Limit articles per feed
                    entries = feed.entries[:settings.MAX_ARTICLES_PER_FEED]
                    
                    for entry in entries:
                        article = {
                            "title": entry.get("title", "No Title"),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                            "summary": entry.get("summary", "") or entry.get("description", ""),
                            "source": feed.feed.get("title", "Unknown Source"),
                            "domain": category,
                            "content": "" # Placeholder for full content if we were to scrape it
                        }
                        
                        # Some feeds put content in 'content' list
                        if 'content' in entry:
                            article['content'] = entry.content[0].value
                        
                        all_articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Failed to fetch from {url}: {e}")
                    
        logger.info(f"Fetched {len(all_articles)} articles in total.")
        return all_articles
