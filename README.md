<div align="center">

# J.A.R.V.I.S.
### Just A Rather Very Intelligent System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-00E5FF?style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/AI-Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![RAG](https://img.shields.io/badge/RAG-ChromaDB-FF4B4B?style=for-the-badge&logo=google-cloud&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Next-Generation Personal Assistant with Neural Interface**

</div>

---

## 🚀 **Overview**

**J.A.R.V.I.S.** is a modular, AI-powered personal assistant designed to automate tasks, retain knowledge, answer complex queries, and interact via a futuristic Graphical User Interface (GUI). Unlike traditional chatbots, Jarvis mimics a human thought process using a **"Three-Stage Brain"** architecture.

> *"I am not just a program. I am a system designed to evolve."*

---

## 📸 **Demo**

*(Add a GIF of Jarvis running here)*
> *Experience the fluid animations and real-time voice interaction.*

---

## 🧠 **Architecture**

Jarvis operates on a sophisticated multi-agent system:

```mermaid
graph TD;
    User[User Input] -->|Voice/Text| Cortex[Cortex (Classifier)];
    Cortex -->|Simple Command| SystemOps[System Operations];
    Cortex -->|Complex Query| DeepMind[Deep Mind (LLM)];
    Cortex -->|Knowledge Query| RAG[RAG Engine];
    
    SystemOps -->|Execute| OS[Operating System];
    DeepMind -->|Reasoning| Response[Response Generation];
    RAG -->|Retrieve| VectorDB[(ChromaDB Knowledge)];
    VectorDB -->|Context| DeepMind;
    
    OS --> GUI[Visual Feedback];
    Response --> GUI;
```

### 1. The Cortex (Classifier)
Uses **Meta-Llama-3-8B-Instruct** to instantly categorize your intent:
- **SYSTEM_ACTION**: Controls your PC (Volume, Apps, etc.).
- **WEB_SEARCH**: Browses the live internet for data.
- **THINK_AND_ANSWER**: Engages in deep reasoning.
- **RETRIEVAL**: Fetches stored knowledge from the news database.

### 2. The Deep Mind (Reasoner)
Uses **Meta-Llama-3.3-70B-Instruct** for high-level problem solving, coding assistance, and creative writing. It can now access the RAG system to answer questions about recent events without hallucinations.

### 3. The Knowledge Base (RAG System)
A dedicated subsystem that:
- **Fetches** daily news from global RSS feeds (Tech, Science, Finance).
- **Embeds** articles using `sentence-transformers`.
- **Stores** vectors in a local **ChromaDB**.
- **Retrieves** context for the Deep Mind to answer "current events" questions.

---

## ✨ **Features**

### 🤖 **Core Intelligence**
- **🗣️ Voice Response**: Natural TTS with interrupt capability.
- **🧠 Contextual Memory**: Remembers past interactions (in-session).
- **📚 Daily Knowledge**: Auto-updates with global news every morning.

### 💻 **System Control**
- *"Turn up the volume"*
- *"Open Calculator"*
- *"Mute audio"*

### 🌐 **Web Automation**
- **Autonomous Browsing**: Google Search via Selenium.
- **News Aggregation**: Summarizes top stories from TechCrunch, BBC, Bloomberg, etc.

### 🎨 **Visual Interface**
- **Cyberpunk UI**: Dark/Cyan aesthetics with `customtkinter`.
- **Live Status**: Real-time listening indicators and system stats.
- **Thread-Safe**: Optimized background processing for a lag-free experience.

---

## 🛠️ **Installation**

### Prerequisites
- Python 3.10+
- [Git](https://git-scm.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/kiruthik04/Jarvis.git
cd Jarvis
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
# Windows
./venv/Scripts/Activate.ps1
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# News System specific dependencies
pip install -r jarvis_news_system/requirements.txt
```

### 4. Configure Environment
1.  Rename `.env.example` to `.env`.
2.  Add your [Hugging Face Access Token](https://huggingface.co/settings/tokens).
    ```ini
    HUGGINGFACE_API_TOKEN=hf_your_token_here
    ```

---

## ⏯️ **Usage**

### 1. Run the Main Assistant
Launch the GUI and voice interface:
```bash
python main.py
```

### 2. Manage Knowledge Base (News System)
Jarvis's knowledge base runs as a separate module to keep the main app lightweight.

**Manual Update (Run Now):**
```bash
python -m jarvis_news_system.main run-now
```

**Start Daily Scheduler:**
```bash
python -m jarvis_news_system.main schedule
```

### 3. Voice Commands to Try
- **"Open Google"** → Launches Chrome.
- **"Who is the CEO of Tesla?"** → Searches the web.
- **"What is the latest in AI news?"** → RAG retrieval from local DB.
- **"Write a python script to sort a list."** → Deep code generation.

---

## 📂 **Project Structure**

```
Jarvis/
├── src/
│   ├── actions/        # Tools (Voice, Browser, System)
│   ├── brain/          # AI Models (Classifier, LLM)
│   ├── ui/             # CustomTkinter Interface
│   └── config.py       # Global Settings
├── jarvis_news_system/ # RAG Subsystem
│   ├── ingestion/      # RSS Fetchers
│   ├── processing/     # Summarizers
│   ├── embeddings/     # Vector Generation
│   ├── vector_store/   # ChromaDB
│   └── retrieval/      # RAG Logic
├── main.py             # App Entry Point
├── check_system.py     # Diagnostics
└── requirements.txt    # Dependencies
```

---

<div align="center">
    <sub>Built with ❤️ by Kiruthik</sub>
</div>
