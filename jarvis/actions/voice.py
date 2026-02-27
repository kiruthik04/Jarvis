import pyttsx3
import threading
import queue
import time

class VoiceEngine:
    def __init__(self):
        self.queue = queue.Queue()
        self.is_running = True
        self.current_engine = None
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def speak(self, text):
        self.queue.put(text)

    def stop_speaking(self):
        # 1. Clear pending messages
        with self.queue.mutex:
            self.queue.queue.clear()
        
        # 2. Stop current utterance
        if self.current_engine:
            try:
                self.current_engine.stop()
            except Exception as e:
                print(f"Error stopping TTS: {e}")

    def _worker(self):
        while self.is_running:
            try:
                # Wait for text (blocking)
                text = self.queue.get()
                if text is None: break
                
                print(f"[DEBUG] Speaking: {text[:20]}...")
                
                # Re-initialize engine each time
                self.current_engine = pyttsx3.init()
                self.current_engine.setProperty('rate', 170)
                self.current_engine.say(text)
                self.current_engine.runAndWait()
                
                # Cleanup
                del self.current_engine
                self.current_engine = None
                
                self.queue.task_done()
            except Exception as e:
                print(f"TTS Loop Error: {e}")
                
    def stop(self):
        self.is_running = False
        self.queue.put(None)
