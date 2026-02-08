import sqlite3
import json
import time
import os

class MemoryManager:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database for memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Key-Value Store for Preferences/Facts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp REAL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Memory Init Error: {e}")

    def remember(self, key, value):
        """Store a fact or preference."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = time.time()
            cursor.execute('''
                INSERT OR REPLACE INTO memory (key, value, timestamp)
                VALUES (?, ?, ?)
            ''', (key, value, timestamp))
            
            conn.commit()
            conn.close()
            return f"I'll remember that {key} is {value}."
        except Exception as e:
            return f"Failed to remember: {e}"

    def recall(self, key):
        """Retrieve a specific fact."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Recall Error: {e}")
            return None

    def get_all_context(self):
        """Retrieve all stored memories as a text block for the LLM context."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM memory')
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return ""
            
            context_lines = ["User Context & Memory:"]
            for key, value in rows:
                context_lines.append(f"- {key}: {value}")
            
            return "\n".join(context_lines)
        except Exception as e:
            print(f"Context Retrieval Error: {e}")
            return ""

    def forget(self, key):
        """Delete a specific memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM memory WHERE key = ?', (key,))
            commit = conn.total_changes > 0
            
            conn.commit()
            conn.close()
            
            return f"I have forgotten {key}." if commit else f"I didn't have any memory of {key}."
        except Exception as e:
            return f"Failed to forget: {e}"
