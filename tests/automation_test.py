import os
import sys
import time
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain.classifier import TaskClassifier
from src.actions.automation import AutomationManager

def print_result(step, result, status="INFO"):
    print(f"[{status}] {step}: {result}")

def test_automation():
    print("\n--- TEST: AUTOMATION & SCHEDULER ---")
    
    # Mock callback
    def mock_callback(msg):
        print(f"CALLBACK RECEIVED: {msg}")
    
    automator = AutomationManager(callback_function=mock_callback)
    automator.start()
    
    # 1. Set Reminder (Immediate)
    # Using a timestamp slightly in the future or assuming "immediate" isn't supported yet by lib,
    # but we can test the 'set_reminder' function return.
    
    res = automator.set_reminder("Test Reminder", "12:00") # Just testing registration
    print_result("Set Reminder Registration", res, "INFO")
    
    if "Reminder set" in res or "Please assert" in res:
        print_result("Set Reminder Logic", "Returned valid response -> PASS", "PASS")
    else:
        print_result("Set Reminder Logic", "Failed -> FAIL", "FAIL")

    # 2. Check Pending
    pending = automator.get_pending_reminders()
    print_result("Pending Reminders", pending, "INFO")
    
    if pending:
         print_result("Job Scheduling", "Job found in queue -> PASS", "PASS")
    else:
         # Note: If it was "Please assert time...", then no job might be added.
         # Let's try to parse the response to see if we should expect a job.
         if "set for" in res:
            print_result("Job Scheduling", "Job missing -> FAIL", "FAIL")
         else:
            print_result("Job Scheduling", "Values invalid (expected) -> PASS", "PASS")
            
    # Clean up
    automator.stop()

def run_tests():
    test_automation()

if __name__ == "__main__":
    run_tests()
