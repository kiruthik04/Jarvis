from sentence_transformers import SentenceTransformer
import logging
from typing import List, Union
from jarvis_news_system.config import settings

logger = logging.getLogger(__name__)

class NewsEmbedder:
    """
    Generates embeddings for news articles using Sentence Transformers.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NewsEmbedder, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Singleton pattern for model loading to avoid reloading
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string.
        """
        if not text:
            return []
        try:
            return self._model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a batch of strings.
        """
        if not texts:
            return []
        try:
            return self._model.encode(texts).tolist()
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            return []
