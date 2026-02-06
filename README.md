
<div align="center">

# J.A.R.V.I.S.
### Just A Rather Very Intelligent System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-00E5FF?style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/AI-Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Next-Generation Personal Assistant with Neural Interface**

</div>

---

## 🚀 Overview

**J.A.R.V.I.S.** is a modular, AI-powered personal assistant designed to automate tasks, answer complex queries, and interact via a futuristic Graphical User Interface (GUI). Unlike traditional chatbots, Jarvis mimics a human thought process using a **"Two-Stage Brain"** architecture.

> *"I am not just a program. I am a system designed to evolve."*

## 🧠 Architecture

### 1. The Classifier (Cortex)
Uses **Meta-Llama-3-8B-Instruct** (via Hugging Face API) to instantly categorize your intent into strict logic streams:
- **SYSTEM_ACTION**: Controls your PC (Volume, Apps, etc.).
- **WEB_SEARCH**: Browses the live internet for data.
- **THINK_AND_ANSWER**: Engages in deep reasoning for complex questions.

### 2. The Reasoner (Deep Mind)
Uses **Meta-Llama-3.3-70B-Instruct** for high-level problem solving, coding assistance, and creative writing.

### 3. The Interface (Visual & Audio)
- **GUI**: A `customtkinter` based Dark/Cyan aesthetics interface.
- **Voice**: Full TTS (Text-to-Speech) integration using `pyttsx3` with interrupt capability.

---

## ✨ Features

- **🗣️ Voice Response**: Jarvis speaks back to you (Toggleable).
- **🛑 Interrupt Capability**: "Stop Audio" button for immediate silence.
- **💻 System Control**: 
  - *"Turn up the volume"*
  - *"Open Calculator"*
  - *"Mute audio"*
- **🌐 Web Automation**: Autonomous Google Search via Selenium.
- **🎨 Modern UI**: cyberpunk-inspired interface with real-time status updates.
- **⚡ Thread-Safe**: Optimized background processing for a lag-free experience.

---

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/kiruthik04/Jarvis.git
    cd Jarvis
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    ./venv/Scripts/Activate.ps1  # Windows
    # source venv/bin/activate # Mac/Linux
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    - Rename `.env.example` to `.env`.
    - Add your [Hugging Face Access Token](https://huggingface.co/settings/tokens).
    ```ini
    HUGGINGFACE_API_TOKEN=hf_your_token_here
    ```

---

## ⏯️ Usage

Run the main system:
```bash
python main.py
```

### Commands to try:
- **"Open Google"** → Launches Chrome.
- **"Who is the CEO of Tesla?"** → Searches the web.
- **"Write a poem about code."** → Uses the reasoning brain.
- **"Mute system volume."** → Controls OS media keys.

---

## 📂 Project Structure

```
Jarvis/
├── src/
│   ├── actions/        # Tool definitions (Voice, Browser, System)
│   ├── brain/          # AI Models (Classifier, LLM)
│   ├── ui/             # CustomTkinter Interface
│   └── config.py       # Settings loader
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── setup.py            # Package config
```

---

<div align="center">
    <sub>Built with ❤️ by Kiruthik</sub>
</div>
