import os
import platform
import pyautogui
import time

class SystemOps:
    @staticmethod
    def execute_intent(intent, parameters=None):
        """
        Executes a system level intent.
        intent: string (e.g., 'open_app', 'volume_up')
        parameters: dict
        """
        print(f"Executing System Intent: {intent} with params: {parameters}")
        
        # Normalize intent
        normalized_intent = intent.lower().replace(" ", "_").strip()
        
        # Mapping common variations
        if "mute" in normalized_intent:
            normalized_intent = "volume_mute"
        elif "increase" in normalized_intent or "up" in normalized_intent or "raise" in normalized_intent:
            normalized_intent = "volume_increase"
        elif "decrease" in normalized_intent or "down" in normalized_intent or "lower" in normalized_intent or "reduce" in normalized_intent:
            normalized_intent = "volume_decrease"
        elif "open" in normalized_intent and ("app" in normalized_intent or "application" in normalized_intent):
            normalized_intent = "open_application"
        elif "screenshot" in normalized_intent:
             normalized_intent = "take_screenshot"
            
        print(f"Normalized Intent: {normalized_intent}") # Debug
        
        # --- VOLUME CONTROL ---
        if normalized_intent == "volume_increase":
            # Press volume up 5 times for a noticeable change
            for _ in range(5):
                pyautogui.press("volumeup")
                
            for _ in range(5):
                pyautogui.press("volumeup")
                
        elif normalized_intent == "volume_decrease":
            for _ in range(5):
                pyautogui.press("volumedown")
                
        elif normalized_intent == "volume_mute":
            pyautogui.press("volumemute")

        # --- APP MANAGEMENT ---
        elif normalized_intent == "open_application":
            app_name = parameters.get("app_name") or parameters.get("application name") or parameters.get("app") or ""
            app_name = app_name.lower()
            SystemOps._open_app(app_name)

        # --- BROWSER SHORTCUTS ---
        elif normalized_intent == "open_browser":
             os.system("start chrome")

        elif normalized_intent == "take_screenshot":
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            print("Screenshot saved to screenshot.png")

        else:
            print(f"Unknown system intent: {intent}")

    @staticmethod
    def _open_app(app_name):
        if "notepad" in app_name:
            os.system("notepad")
        elif "calc" in app_name:
            os.system("calc")
        elif "chrome" in app_name:
            os.system("start chrome")
        elif "explorer" in app_name:
            os.system("explorer")
        elif "cmd" in app_name or "terminal" in app_name:
            os.system("start cmd")
        else:
            # Generic attempt to start via windows run
            try:
                os.system(f"start {app_name}")
            except:
                print(f"Could not open {app_name}")
