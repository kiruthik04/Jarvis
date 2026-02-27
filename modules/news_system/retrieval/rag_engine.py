from jarvis_news_system.embeddings.embedder import NewsEmbedder
from jarvis_news_system.vector_store.store import VectorStore
from jarvis_news_system.config import settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Orchestrates the retrieval of relevant context from the vector store.
    """
    def __init__(self):
        self.embedder = NewsEmbedder()
        self.store = VectorStore()

    def retrieve_context(self, query: str, top_k: int = settings.TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """
        Retrieves relevant documents for a given query.
        """
        query_embedding = self.embedder.embed_text(query)
        if not query_embedding:
            logger.warning("Empty embedding for query.")
            return []
        
        # Query requires a list of embeddings
        results = self.store.query(query_embeddings=[query_embedding], n_results=top_k)
        
        if not results or not results['documents']:
            return []
            
        # Format results
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else []
        
        retrieved_content = []
        for i, doc in enumerate(documents):
            # Optional threshold filtering can be added here
            item = {
                "content": doc,
                "metadata": metadatas[i]
            }
            if i < len(distances):
                 item["distance"] = distances[i]
                 
            retrieved_content.append(item)
            
        return retrieved_content

    def format_context_for_llm(self, retrieved_items: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved items into a string context block for the LLM.
        """
        context_parts = []
        for item in retrieved_items:
            meta = item['metadata']
            source = meta.get('source', 'Unknown')
            date = meta.get('published', 'Unknown Date')
            content = item['content']
            context_parts.append(f"Source: {source} ({date})\nContent: {content}\n")
            
        return "\n---\n".join(context_parts)
