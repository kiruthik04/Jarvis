"""
main_headless.py
────────────────
Runs Jarvis with NO GUI window.
Only the voice listener + brain + TTS pipeline starts.
Say "Hey Jarvis <command>" to interact.
"""

import sys
import time
import threading

from jarvis.brain.classifier import TaskClassifier
from jarvis.brain.llm import ReasoningBrain
from jarvis.actions.voice_manager import VoiceManager
from jarvis.actions.voice_input import VoiceInputListener
from jarvis.brain.memory import MemoryManager
from jarvis.actions.system_ops import SystemOps
from jarvis.actions.browser import BrowserManager
from jarvis.actions.automation import AutomationManager
from jarvis.config import Config


class HeadlessJarvis:
    """Full Jarvis pipeline (voice in → brain → voice out) — no GUI."""

    def __init__(self):
        print("[Jarvis] Initializing headless mode...")

        self.classifier = TaskClassifier()
        self.brain = ReasoningBrain()
        self.memory = MemoryManager()
        self.browser = BrowserManager()

        # Voice output — resumes listener after speaking
        self.voice = VoiceManager(on_speech_complete=self._resume_listener)

        # Reminders / automation
        self.automation = AutomationManager(
            callback_function=lambda msg: self._speak(msg)
        )
        self.automation.start()

        # Gmail (optional)
        if Config.GMAIL_ENABLED:
            from jarvis.actions.gmail import GmailManager
            self.gmail = GmailManager()
            print("[Jarvis] Gmail & Calendar module loaded.")
        else:
            self.gmail = None

        # Voice input listener
        self.voice_input = VoiceInputListener(callback_function=self._on_command)
        self.voice_input.start()

        self._speak("Systems nominal. I am listening.")
        print("[Jarvis] Headless mode active. Say 'Hey Jarvis...' to interact.")
        print("[Jarvis] Press Ctrl+C to exit.\n")

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────

    def _speak(self, text: str, emotion: str = "NEUTRAL"):
        """Pause listener while speaking so Jarvis doesn't hear itself."""
        self.voice_input.pause()
        self.voice.speak(text, emotion)

    def _resume_listener(self):
        self.voice_input.resume()
        print("[Jarvis] Listening...")

    # ──────────────────────────────────────────────
    # Command handler
    # ──────────────────────────────────────────────

    def _on_command(self, command: str):
        """Called by VoiceInputListener when a wake-word command is detected."""
        print(f"\n[You (Voice)] {command}")
        self.voice_input.pause()
        threading.Thread(target=self._run_pipeline, args=(command,), daemon=True).start()

    def _run_pipeline(self, user_input: str):
        try:
            classification = self.classifier.classify(user_input)
            task_type = classification.get("task_type")
            print(f"[Jarvis] Task type: {task_type}")

            if task_type == "SYSTEM_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                if intent == "system_status":
                    result = SystemOps.run_diagnostics()
                else:
                    result = SystemOps.execute_intent(intent, params)
                self._speak(result)

            elif task_type == "MEMORY_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                key = params.get("key")
                value = params.get("value")
                if intent == "remember" and key and value:
                    msg = self.memory.remember(key, value)
                elif intent == "forget" and key:
                    msg = self.memory.forget(key)
                else:
                    msg = "I didn't catch what you wanted me to remember."
                self._speak(msg)

            elif task_type == "AUTOMATION_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                if intent == "set_reminder":
                    msg_text = params.get("message")
                    time_str = params.get("time")
                    if msg_text and time_str:
                        res = self.automation.set_reminder(msg_text, time_str)
                        self._speak(res)
                    else:
                        self._speak("I need both a message and a time for the reminder.")
                elif intent == "list_reminders":
                    pending = self.automation.get_pending_reminders()
                    self._speak(str(pending) if pending else "No pending reminders.")

            elif task_type == "WEB_SEARCH":
                query = classification.get("query")
                print(f"[Jarvis] Searching: {query}")
                self._speak(f"Searching for {query}.")
                self.browser.search_google(query)
                url = self.browser.get_first_search_result(query)
                if url:
                    content = self.browser.extract_text(url)
                    if content and len(content) > 100:
                        summary = self.brain.think(
                            f"Summarize the following text for the query '{query}':\n\n{content[:3000]}"
                        )
                        self._speak(summary)
                    else:
                        self._speak("I found a result but couldn't extract content.")
                else:
                    self._speak("I couldn't find a direct result.")

            elif task_type == "THINK_AND_ANSWER":
                mem_context = self.memory.get_all_context()
                answer = self.brain.think(user_input, memory_context=mem_context)
                self._speak(answer)

            elif task_type == "EMAIL_ACTION":
                if not self.gmail:
                    self._speak("Gmail is disabled. Set GMAIL_ENABLED to true in the .env file.")
                else:
                    intent = classification.get("intent", "")
                    params = classification.get("parameters", {})
                    if intent == "read_emails":
                        emails = self.gmail.read_unread_emails(max_results=5)
                        if isinstance(emails, list):
                            raw = "\n".join(
                                [f"From: {e['sender']} Subject: {e['subject']} Preview: {e['snippet']}" for e in emails]
                            )
                            summary = self.brain.think(f"Summarize these emails briefly:\n\n{raw}")
                            self._speak(summary)
                    elif intent == "get_calendar":
                        events = self.gmail.get_upcoming_events(max_results=7)
                        if isinstance(events, list):
                            raw = "\n".join([f"{e['title']} starts {e['start']}" for e in events])
                            summary = self.brain.think(f"Narrate these calendar events:\n\n{raw}")
                            self._speak(summary)
                    else:
                        self._speak("I didn't understand that email request.")

            else:
                answer = self.brain.think(user_input)
                self._speak(answer)

        except Exception as e:
            print(f"[Jarvis] Pipeline Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._resume_listener()

    def run_forever(self):
        """Block the main thread so the background threads keep running."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Jarvis] Shutting down...")
            self.voice_input.stop()
            self.automation.stop()
            sys.exit(0)


if __name__ == "__main__":
    jarvis = HeadlessJarvis()
    jarvis.run_forever()
