import json
import os
import time
from datetime import datetime

class Logger:
    def __init__(self, log_file="data/logs/jarvis_activity.json"):
        self.log_file = log_file
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        directory = os.path.dirname(self.log_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Initialize file if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_interaction(self, user_input: str, classification: dict = None,
                         action_taken: str = None, response: str = None,
                         latency: float = 0.0,
                         # Legacy aliases
                         action: str = None, response_text: str = None):
        """Log a completed pipeline interaction.
        Accepts both old (action=, response=) and new (action_taken=, response_text=) naming.
        """
        resolved_action   = action_taken or action or "unknown"
        resolved_response = response or response_text or ""

        entry = {
            "timestamp":      datetime.now().isoformat(),
            "user_input":     user_input,
            "classification": classification or {},
            "action_taken":   resolved_action,
            "response":       resolved_response,
            "latency_ms":     round(latency * 1000, 2)
        }

        try:
            with open(self.log_file, "r+") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
                logs.append(entry)
                f.seek(0)
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Logging Error: {e}")

    def log_error(self, source, message):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "source": source,
            "message": message
        }
        self._append_entry(entry)

    def _append_entry(self, entry):
         try:
            with open(self.log_file, "r+") as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
                logs.append(entry)
                f.seek(0)
                json.dump(logs, f, indent=4)
         except:
             pass
