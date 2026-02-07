import os
import platform
import pyautogui
import time
import subprocess

class SystemOps:
    @staticmethod
    def execute_intent(intent, parameters=None):
        """
        Executes a system level intent.
        Returns a string message indicating the result.
        """
        if parameters is None:
            parameters = {}
            
        print(f"Executing System Intent: {intent} with params: {parameters}")
        
        # 1. Normalize Intent
        normalized_intent = intent.lower().replace(" ", "_").strip()
        
        # 2. Normalize Parameters (Keys to lowercase)
        norm_params = {k.lower(): v for k, v in parameters.items()}
        
        # --- INTENT MAPPING ---
        
        if "open" in normalized_intent:
            if "setting" in normalized_intent:
                normalized_intent = "open_settings"
            elif "app" in normalized_intent or "application" in normalized_intent:
                normalized_intent = "open_application"
            else:
                 normalized_intent = "open_application" 

        if "mute" in normalized_intent:
            normalized_intent = "volume_mute"
        elif any(x in normalized_intent for x in ["increase", "up", "raise"]):
            normalized_intent = "volume_increase"
        elif any(x in normalized_intent for x in ["decrease", "down", "lower", "reduce"]):
            normalized_intent = "volume_decrease"
        elif "wifi" in normalized_intent or "network" in normalized_intent:
             if "show" in normalized_intent or "list" in normalized_intent:
                 normalized_intent = "show_wifi_networks"
             else:
                 normalized_intent = "change_wifi_network"
            
        elif "screenshot" in normalized_intent:
             normalized_intent = "take_screenshot"

        print(f"Normalized Intent: {normalized_intent}") # Debug
        
        # --- EXECUTION ---

        # Volume
        if normalized_intent == "volume_increase":
            for _ in range(5): pyautogui.press("volumeup")
            return "Volume increased."
                
        elif normalized_intent == "volume_decrease":
            for _ in range(5): pyautogui.press("volumedown")
            return "Volume decreased."
                
        elif normalized_intent == "volume_mute":
            pyautogui.press("volumemute")
            return "Audio toggled."

        # App Management
        elif normalized_intent == "open_application":
            app_name = norm_params.get("app_name") or \
                       norm_params.get("application name") or \
                       norm_params.get("application") or \
                       norm_params.get("app") or \
                       norm_params.get("name") or ""
            
            if "setting" in app_name.lower():
                 return SystemOps._open_settings()
            else:
                 return SystemOps._open_app(app_name)

        elif normalized_intent == "open_settings":
            return SystemOps._open_settings()

        # Browser
        elif normalized_intent == "open_browser":
             subprocess.Popen("start chrome", shell=True)
             return "Opening Google Chrome."

        # Screenshot
        elif normalized_intent == "take_screenshot":
            filename = f"screenshot_{int(time.time())}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            print(f"Screenshot saved to {filename}")
            return f"Screenshot saved as {filename}."

        # Wi-Fi
        elif normalized_intent == "change_wifi_network":
             ssid = norm_params.get("network_name") or \
                    norm_params.get("ssid") or \
                    norm_params.get("wifi") or \
                    norm_params.get("network") or \
                    norm_params.get("name") or ""
             
             if ssid:
                 return SystemOps._connect_wifi(ssid)
             else:
                 return "No network name specified."

        # Show Wi-Fi Networks
        elif normalized_intent == "show_wifi_networks":
             return SystemOps._list_wifi_networks()

        else:
            return f"I'm sorry, I don't know how to execute: {intent}"

    @staticmethod
    def _open_settings():
        try:
            subprocess.Popen("start ms-settings:", shell=True)
            return "Opening Windows Settings."
        except Exception as e:
            return f"Failed to open settings: {e}"

    @staticmethod
    def _open_app(app_name):
        app_name = app_name.lower().strip()
        print(f"Attempting to open app: '{app_name}'")
        
        if not app_name:
            return "No application name provided."

        try:
            if "notepad" in app_name:
                subprocess.Popen("notepad.exe")
            elif "calc" in app_name:
                subprocess.Popen("calc.exe")
            elif "chrome" in app_name or "google" in app_name:
                subprocess.Popen("start chrome", shell=True)
            elif "explorer" in app_name or "file" in app_name:
                subprocess.Popen("explorer.exe")
            elif "cmd" in app_name or "terminal" in app_name:
                subprocess.Popen("start cmd", shell=True)
            elif "code" in app_name or "vscode" in app_name:
                try:
                    subprocess.Popen("code") 
                except:
                    subprocess.Popen("start code", shell=True)
            elif "code" in app_name or "vscode" in app_name:
                try:
                    subprocess.Popen("code") 
                except:
                    subprocess.Popen("start code", shell=True)
            elif "whatsapp" in app_name:
                subprocess.Popen("start whatsapp:", shell=True)
            elif "spotify" in app_name:
                subprocess.Popen("start spotify:", shell=True)
            elif "telegram" in app_name:
                subprocess.Popen("start telegram:", shell=True)
            else:
                 subprocess.Popen(f"start {app_name}", shell=True)
            
            return f"Opening {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"

    @staticmethod
    def _connect_wifi(ssid):
        print(f"Connecting to Wi-Fi: {ssid}")
        try:
            cmd = f'netsh wlan connect name="{ssid}"'
            subprocess.run(cmd, shell=True, check=True)
            return f"Connecting to Wi-Fi network: {ssid}."
        except subprocess.CalledProcessError as e:
            # If failed, list available profiles for debugging
            return SystemOps._list_wifi_networks()

    @staticmethod
    def _list_wifi_networks():
        try:
            # Show visible networks (scanned)
            result = subprocess.check_output("netsh wlan show networks", shell=True).decode()
            
            # Extract SSIDs cleanly
            networks = []
            for line in result.split("\n"):
                if "SSID" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid: # Filter empty SSIDs
                            networks.append(ssid)
            
            if networks:
                # Show up to 10 networks
                count = len(networks)
                display_list = ", ".join(networks[:10])
                return f"Found {count} networks. Top ones: {display_list}"
            else:
                return "No visible Wi-Fi networks found."
        except Exception as e:
            return f"Could not list networks: {e}"
