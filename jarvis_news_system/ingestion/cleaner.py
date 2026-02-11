from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

class TextCleaner:
    """
    Utility class to clean and normalize text from HTML content.
    """
    
    @staticmethod
    def clean_html(html_content: str) -> str:
        """
        Removes HTML tags and normalizes whitespace.
        """
        if not html_content:
            return ""
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text(separator=" ")
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_content

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Basic text normalization.
        """
        if not text:
            return ""
        # Further normalization logic can be added here (e.g. unicode normalization)
        return text.strip()
