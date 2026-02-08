import sys
import os
import time
sys.path.append(os.getcwd())

from src.utils.logger import Logger
from src.actions.system_ops import SystemOps

def test_logger():
    print("Testing Logger...")
    logger = Logger()
    logger.log_interaction("Test Input", {"task_type": "TEST"}, "TEST_ACTION", "Test Response", 0.123)
    
    if os.path.exists("logs/jarvis_activity.json"):
        print("[PASS] Log file created.")
    else:
        print("[FAIL] Log file not found.")

def test_diagnostics():
    print("\nTesting Diagnostics...")
    result = SystemOps._get_system_status()
    print(f"Diagnostics Result:\n{result}")
    
    if "Internet:" in result and "CPU Load:" in result:
        print("[PASS] Diagnostics returned valid report.")
    else:
        print("[FAIL] Diagnostics missing key info.")

if __name__ == "__main__":
    test_logger()
    test_diagnostics()
