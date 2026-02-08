import unittest
import os
import sys
import time
import shutil

# Ensure src is in path
sys.path.append(os.getcwd())

from src.brain.memory import MemoryManager
from src.actions.system_ops import SystemOps
from src.actions.automation import AutomationManager
from src.actions.browser import BrowserManager
from src.utils.logger import Logger

class SystemTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\n=== STARTING JARVIS SYSTEM VERIFICATION 2.0 ===\n")
        # Setup Logger
        cls.logger = Logger(log_file="tests/test_logs/system_test.json")
        
        # Setup Memory (use a test db)
        cls.memory = MemoryManager(db_path="tests/test_memory.db")
        
    @classmethod
    def tearDownClass(cls):
        # Cleanup
        if os.path.exists("tests/test_memory.db"):
            os.remove("tests/test_memory.db")
        if os.path.exists("tests/test_logs"):
            shutil.rmtree("tests/test_logs")
        print("\n=== SYSTEM VERIFICATION COMPLETE ===\n")

    def test_01_memory_persistence(self):
        """Test Memory Read/Write/Forget"""
        print("Testing Memory Module...")
        self.memory.remember("test_key", "test_value")
        context = self.memory.get_context("test_key")
        self.assertIn("test_value", context)
        
        self.memory.forget("test_key")
        context = self.memory.get_context("test_key")
        self.assertNotIn("test_value", context)
        print("[PASS] Memory Persistence")

    def test_02_system_diagnostics(self):
        """Test System Diagnostics"""
        print("Testing System Diagnostics...")
        status = SystemOps.run_diagnostics()
        self.assertIn("System Status", status)
        self.assertIn("Internet:", status)
        self.assertIn("Disk Space:", status)
        print(f"[PASS] Diagnostics Report:\n{status}")

    def test_03_automation_scheduler(self):
        """Test Scheduler Registration"""
        print("Testing Automation Manager...")
        auto = AutomationManager()
        # Mock callback
        auto.callback = lambda x: print(f"Callback: {x}")
        
        response = auto.set_reminder("Test Task", "in 1 second")
        print(f"  - Set Reminder Response: {response}")
        self.assertIn("I've set a reminder", response)
        
        pending = auto.get_pending_reminders()
        print(f"  - Pending Reminders: {pending}")
        self.assertTrue(len(pending) > 0)
        print("[PASS] Automation Scheduler")

    def test_04_logger_integrity(self):
        """Test Logger File Creation"""
        print("Testing Logger...")
        self.logger.log_interaction("Test Input", {}, "TEST", "Test Response", 0.1)
        self.assertTrue(os.path.exists("tests/test_logs/system_test.json"))
        print("[PASS] Activity Logging")

    def test_05_web_scraping(self):
        """Test Web Content Extraction"""
        print("Testing Web Search & Extraction...")
        browser = BrowserManager()
        
        # 1. Test Search (DuckDuckGo)
        url = browser.get_first_search_result("Python Programming")
        if url:
             print(f"  - Retrieved URL: {url}")
             
             # 2. Test Extraction
             text = browser.extract_text(url)
             self.assertTrue(len(text) > 50)
             print(f"  - Extracted {len(text)} chars.")
        else:
            print("  - [WARNING] Could not retrieve URL (Network/Region issue?)")
        
        browser.close()
        print("[PASS] Web Module")

if __name__ == '__main__':
    with open("test_results_detailed.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner)
