from jarvis_news_system.ingestion.fetcher import NewsFetcher
from jarvis_news_system.ingestion.cleaner import TextCleaner
from jarvis_news_system.processing.summarizer import NewsSummarizer
from jarvis_news_system.embeddings.embedder import NewsEmbedder
from jarvis_news_system.vector_store.store import VectorStore
import logging
import time

logger = logging.getLogger(__name__)

def run_daily_update():
    """
    Orchestrates the daily news update:
    1. Fetch news from RSS
    2. clean and summarize
    3. Embed
    4. Store in Vector DB
    """
    start_time = time.time()
    logger.info("Starting daily news update...")
    
    # 1. Fetch
    try:
        fetcher = NewsFetcher()
        articles = fetcher.fetch_all_news()
        
        if not articles:
            logger.info("No articles fetched.")
            return
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return

    # 2. Process
    cleaner = TextCleaner()
    summarizer = NewsSummarizer()
    embedder = NewsEmbedder()
    
    documents = [] # Content to store
    embeddings = [] # Vectors
    metadatas = [] # Metadata
    ids = [] # Unique IDs
    
    processed_count = 0
    
    logger.info("Processing articles...")
    for article in articles:
        try:
            # Clean text
            article['summary'] = cleaner.clean_html(article.get('summary', ''))
            article['title'] = cleaner.clean_html(article.get('title', ''))
            
            # Summarize if needed
            article = summarizer.process_article(article)
            
            # Check for valid content
            if not article['summary']:
                continue

            # Create text to embed (Title + Summary usually captures the essence)
            text_to_embed = f"{article['title']}: {article['summary']}"
            embedding = embedder.embed_text(text_to_embed)
            
            if embedding:
                documents.append(article['summary'])
                embeddings.append(embedding)
                metadatas.append({
                    "title": article['title'],
                    "link": article['link'],
                    "source": article['source'],
                    "domain": article['domain'],
                    "published": article['published']
                })
                # Use link as ID to prevent duplicates.
                # If link is missing, generate a hash or uuid
                ids.append(article['link'] or str(hash(text_to_embed)))
                processed_count += 1
                
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
            
    # 3. Store
    if documents:
        try:
            store = VectorStore()
            store.add_documents(documents, embeddings, metadatas, ids)
            logger.info(f"Successfully stored {len(documents)} articles.")
        except Exception as e:
            logger.error(f"Failed to store documents: {e}")
    else:
        logger.warning("No documents to store after processing.")
    
    elapsed = time.time() - start_time
    logger.info(f"Daily update completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    # Configure logging if run directly
    logging.basicConfig(level=logging.INFO)
    run_daily_update()
