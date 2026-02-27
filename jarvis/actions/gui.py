import pyautogui
import time

class GUIController:
    def __init__(self):
        # Fail-safe: moving mouse to screen corner throws exception
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def type_text(self, text, interval=0.05):
        """Types text with a small delay between keystrokes."""
        print(f"Typing: {text}")
        pyautogui.write(text, interval=interval)

    def press_key(self, key):
        """Presses a single key."""
        pyautogui.press(key)

    def hotkey(self, *keys):
        """Executes a hotkey combination (e.g., 'ctrl', 'c')."""
        pyautogui.hotkey(*keys)

    def click_at(self, x, y):
        """Clicks at specific coordinates."""
        pyautogui.click(x, y)

    def take_screenshot(self, filename="screenshot.png"):
        """Takes a screenshot and saves it."""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename
