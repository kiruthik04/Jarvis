# Jarvis News RAG System

A modular, retrieval-augmented generation (RAG) system that fetches daily global news, processes it, and allows Jarvis to retrieve updated knowledge without retraining the base LLM.

## Features
- **Automated Ingestion**: Fetches news from multiple RSS feeds (Tech, Science, World, Finance).
- **Text Processing**: Cleans HTML and summarizes articles.
- **Vector Embeddings**: Uses `sentence-transformers` for high-quality local embeddings.
- **Vector Database**: Stores knowledge in a local ChromaDB instance.
- **RAG Retrieval**: Retrieves the most relevant news based on semantic similarity.
- **Daily Scheduler**: Runs automatically at a configured time (default 06:00).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    - Edit `config/settings.py` to change RSS feeds, update time, or embedding model.

## Usage

**Important**: Run all commands from the root directory (`d:\Projects\jarvis`).

### 1. Manual Update (Run Now)
To fetch and index news immediately:
```bash
python -m jarvis_news_system.main run-now
```

### 2. Start Scheduler
To keep the system running and updating daily:
```bash
python -m jarvis_news_system.main schedule
```

### 3. Query Knowledge Base
To ask a question based on the indexed news:
```bash
python -m jarvis_news_system.main query "What is the latest in AI?"
```

## Architecture
- `ingestion/`: Fetching and cleaning data.
- `processing/`: Summarization.
- `embeddings/`: Vector generation.
- `vector_store/`: ChromaDB management.
- `retrieval/`: RAG logic.
- `scheduler/`: Job orchestration.
