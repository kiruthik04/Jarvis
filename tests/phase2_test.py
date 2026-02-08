import os
import sys
import time
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain.memory import MemoryManager
from src.actions.system_ops import SystemOps
from src.brain.classifier import TaskClassifier

def print_result(step, result, status="INFO"):
    print(f"[{status}] {step}: {result}")

def test_memory():
    print("\n--- TEST: MEMORY SYSTEM ---")
    mem = MemoryManager("test_memory.db")
    
    # 1. Remember
    print_result("Remembering 'User is testing'", mem.remember("User Status", "Testing Phase 2"))
    
    # 2. Recall
    val = mem.recall("User Status")
    if val == "Testing Phase 2":
        print_result("Recalling 'User Status'", f"Got '{val}' -> PASS", "PASS")
    else:
        print_result("Recalling 'User Status'", f"Got '{val}' -> FAIL", "FAIL")

    # 3. Context Retrieval
    ctx = mem.get_all_context()
    if "Testing Phase 2" in ctx:
        print_result("Context Retrieval", "Contains memory -> PASS", "PASS")
    else:
        print_result("Context Retrieval", f"Missing memory. Context: {ctx} -> FAIL", "FAIL")

    # Clean up
    mem.forget("User Status")
    if os.path.exists("test_memory.db"):
        os.remove("test_memory.db")

def test_system_ops():
    print("\n--- TEST: ADVANCED SYSTEM OPS ---")
    
    # 1. System Status
    status = SystemOps.execute_intent("system_status")
    print_result("System Status Check", status, "INFO")
    if "CPU Usage" in status:
        print_result("System Status Format", "Valid -> PASS", "PASS")
    else:
        print_result("System Status Format", "Invalid -> FAIL", "FAIL")

    # 2. Open & Close Notepad
    print("Opening Notepad...")
    SystemOps.execute_intent("open_application", {"app_name": "notepad"})
    time.sleep(2)
    
    print("Closing Notepad...")
    close_res = SystemOps.execute_intent("close_application", {"app_name": "notepad"})
    print_result("Close Notepad Result", close_res, "INFO")
    
    if "Terminated" in close_res:
         print_result("Close App Logic", "Process Terminated -> PASS", "PASS")
    else:
         print_result("Close App Logic", "Failed to terminate (maybe not open?) -> WARN", "WARN")

def run_tests():
    test_memory()
    test_system_ops()

if __name__ == "__main__":
    run_tests()
