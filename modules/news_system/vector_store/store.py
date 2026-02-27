import chromadb
from chromadb.config import Settings
from jarvis_news_system.config import settings
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Manages interactions with ChromaDB.
    """
    _instance = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                logger.info(f"Initializing Vector Store at {settings.CHROMA_PERSIST_DIRECTORY}")
                self._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
                
                # Check directly if collection exists or create it
                self._collection = self._client.get_or_create_collection(
                    name=settings.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Connected to collection: {settings.COLLECTION_NAME}")
            except Exception as e:
                logger.error(f"Failed to initialize Vector Store: {e}")
                raise

    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Adds documents to the collection.
        """
        if not documents:
            return

        try:
            self._collection.upsert(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Upserted {len(documents)} documents to store.")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")

    def query(self, query_embeddings: List[List[float]], n_results: int = settings.TOP_K_RETRIEVAL) -> Optional[Dict[str, Any]]:
        """
        Queries the collection for similar documents.
        """
        try:
            results = self._collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying store: {e}")
            return None
    
    def count(self) -> int:
        """Returns the number of documents in the collection."""
        return self._collection.count()
