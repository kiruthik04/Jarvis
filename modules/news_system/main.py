import argparse
import schedule
import time
import logging
import sys
from jarvis_news_system.scheduler.daily_job import run_daily_update
from jarvis_news_system.retrieval.rag_engine import RAGEngine
from jarvis_news_system.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Jarvis News RAG System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run Now
    subparsers.add_parser("run-now", help="Run the news ingestion immediately")
    
    # Schedule
    subparsers.add_parser("schedule", help="Start the daily scheduler")
    
    # Query
    query_parser = subparsers.add_parser("query", help="Query the knowledge base")
    query_parser.add_argument("text", type=str, help="Question to ask")
    
    args = parser.parse_args()
    
    if args.command == "run-now":
        run_daily_update()
        
    elif args.command == "schedule":
        logger.info(f"Scheduler started. Running daily at {settings.UPDATE_TIME}")
        schedule.every().day.at(settings.UPDATE_TIME).do(run_daily_update)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    elif args.command == "query":
        try:
            logger.info(f"Querying for: {args.text}")
            rag = RAGEngine()
            results = rag.retrieve_context(args.text, top_k=settings.TOP_K_RETRIEVAL)
            
            if not results:
                print("\nNo relevant news found.")
            else:
                print(f"\nFound {len(results)} relevant articles:\n")
                print("-" * 50)
                for item in results:
                    meta = item['metadata']
                    print(f"TITLE: {meta.get('title', 'No Title')}")
                    print(f"SOURCE: {meta.get('source', 'Unknown')} | {meta.get('published', '')}")
                    print(f"CONTENT: {item['content']}")
                    print("-" * 50)
        except Exception as e:
            logger.error(f"Error during query: {e}")
                
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
