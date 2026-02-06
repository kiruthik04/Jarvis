# Jarvis - Personal AI Assistant

A Python-based personal assistant that uses a "Two-Stage Brain" architecture:
1.  **Local Classifier (Phi-3 via Ollama)**: Decides if a request is a System Action, Web Search, or Logic Question.
2.  **Reasoning Brain (Hugging Face)**: Handles complex logic and reasoning queries.

## Features
- **Strict Intent Classification**: "Think before acting".
- **OS Automation**: Controls apps, keys, and mouse.
- **Web Automation**: Uses Selenium to browse.
- **Scraping**: Uses BeautifulSoup for fast info gathering.

## Setup

1.  **Install Ollama**: [ollama.com](https://ollama.com) and run `ollama pull phi3`.
2.  **Install Python**: Ensure Python 3.10+ is installed.
3.  **Setup Environment**:
    ```bash
    python -m venv venv
    ./venv/Scripts/Activate.ps1
    pip install -r requirements.txt
    ```
4.  **Configure**:
    - Rename `.env.example` to `.env`.
    - Add your Hugging Face Token for better reasoning capabilities.
5.  **Run**:
    ```bash
    python main.py
    ```

## Structure
- `src/brain`: LLM and Classification logic.
- `src/actions`: Tools for GUI, Browser, and System.
- `src/config.py`: Configuration loader.
