import schedule
import time
import threading
import datetime

class AutomationManager:
    def __init__(self, callback_function=None):
        self.running = False
        self.reminders = []
        self.callback = callback_function # Function to call when reminder triggers (e.g., UI notify)
        
    def start(self):
        """Starts the scheduler loop in a background thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_continuously, daemon=True)
            self.thread.start()
            print("  Automation Scheduler Started.")

    def _run_continuously(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        schedule.clear()
        if hasattr(self, "thread") and self.thread.is_alive():
            try:
                self.thread.join(timeout=2.0)
            except Exception:
                pass

    def set_reminder(self, message, time_str):
        """
        Sets a one-time reminder.
        time_str formats: "HH:MM", "10 seconds", "5 minutes"
        """
        try:
            # Handle relative time (e.g., "in 5 minutes") logic needs parsing
            # For simplicity, we'll support "HH:MM" (daily) or simple delays for now if parsed externally.
            # But effectively, we might want a simple "delay" based reminder for "remind me in X".
            
            # Case 1: "HH:MM" 24-hour format
            if ":" in time_str and len(time_str) <= 5:
                schedule.every().day.at(time_str).do(self._trigger_reminder, message).tag(message)
                return f"Reminder set for {time_str}: {message}"
            
            # Case 2: Simple delay
            if "in" in time_str:
                parts = time_str.split()
                # Expected: "in", val, unit
                if len(parts) >= 3:
                     val = int(parts[1])
                     unit = parts[2].lower()
                     
                     if "second" in unit:
                         schedule.every(val).seconds.do(self._trigger_reminder, message).tag(message)
                         return f"I've set a reminder for {val} seconds from now: {message}"
                     elif "minute" in unit:
                         schedule.every(val).minutes.do(self._trigger_reminder, message).tag(message)
                         return f"I've set a reminder for {val} minutes from now: {message}"
            
            return "Please assert time in HH:MM format or 'in X minutes'."
            
            
        except Exception as e:
            return f"Failed to set reminder: {e}"

    def _trigger_reminder(self, message):
        print(f"REMINDER TRIGGERED: {message}")
        if self.callback:
            self.callback(f"REMINDER: {message}")
        
        # Remove after triggering (if one-time) - schedule defaults to repeating
        # To make it one-time, we return schedule.CancelJob
        return schedule.CancelJob

    def get_pending_reminders(self):
        return [job.tags for job in schedule.get_jobs()]
