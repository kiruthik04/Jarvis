from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

class NewsSummarizer:
    """
    Summarizes news articles. 
    Ideally, this would use a local LLM or an API, but for this implementation
    we will use extractive checks and truncation as a fallback.
    """
    def __init__(self):
        pass

    def summarize(self, text: str, max_length: int = 300) -> str:
        """
        Summarizes text by taking the first few sentences or truncating.
        """
        if not text:
            return ""
        
        # Simple sentence-based truncation
        sentences = re.split(r'(?<=[.!?]) +', text)
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence + " "
            else:
                break
        
        return summary.strip() or text[:max_length]

    def process_article(self, article: dict) -> dict:
        """
        Ensures an article has a summary. If not, generates one from content.
        """
        if not article.get("summary") and article.get("content"):
            article["summary"] = self.summarize(article["content"])
        elif not article.get("summary") and not article.get("content"):
             # Last resort: use title as summary if nothing else exists
            article["summary"] = article.get("title", "")
            
        return article
