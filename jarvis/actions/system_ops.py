import os
import platform
import pyautogui
import time
import subprocess
import psutil

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

        # Advanced System Ops
        elif normalized_intent == "close_application":
            app_name = norm_params.get("app_name") or \
                       norm_params.get("application name") or \
                       norm_params.get("application") or \
                       norm_params.get("process") or ""
            if app_name:
                return SystemOps._close_app(app_name)
            else:
                return "Which application should I close?"

        elif normalized_intent == "system_status":
             return SystemOps._get_system_status()

        elif normalized_intent == "power_control":
             action = norm_params.get("action") or "lock" 
             return SystemOps._power_control(action)

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
        app_name = app_name.strip() # Don't lower yet, might be a file path
        print(f"Attempting to open app/file: '{app_name}'")
        
        if not app_name or app_name == "<unknown>" or app_name.lower() == "unknown":
            return "Please specify which application you would like to open."

        try:
            # 1. Try opening as a file or path directly using os.startfile (Windows only)
            if os.path.exists(app_name):
                os.startfile(app_name)
                return f"Opening file: {app_name}"

            # 2. Known App Shortcuts
            app_lower = app_name.lower()
            if "notepad" in app_lower:
                subprocess.Popen("notepad.exe")
            elif "calc" in app_lower:
                subprocess.Popen("calc.exe")
            elif "chrome" in app_lower or "google" in app_lower:
                subprocess.Popen("start chrome", shell=True)
            elif "explorer" in app_lower or "file" in app_lower:
                subprocess.Popen("explorer.exe")
            elif "cmd" in app_lower or "terminal" in app_lower:
                subprocess.Popen("start cmd", shell=True)
            elif "code" in app_lower or "vscode" in app_lower:
                try:
                    subprocess.Popen("code") 
                except:
                    subprocess.Popen("start code", shell=True)
            elif "whatsapp" in app_lower:
                subprocess.Popen("start whatsapp:", shell=True)
            elif "spotify" in app_lower:
                subprocess.Popen("start spotify:", shell=True)
            elif "telegram" in app_lower:
                subprocess.Popen("start telegram:", shell=True)
            else:
                 # Fallback to start command for other apps
                 # Wrap in quotes to handle spaces in title/path
                 subprocess.Popen(f'start "" "{app_name}"', shell=True)
            
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
            # 1. Get Visible Networks
            visible_output = subprocess.check_output("netsh wlan show networks", shell=True).decode("utf-8", errors="ignore")
            visible_networks = []
            for line in visible_output.split("\n"):
                if "SSID" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid: visible_networks.append(ssid)
            
            # 2. Get Saved Profiles
            profile_output = subprocess.check_output("netsh wlan show profiles", shell=True).decode("utf-8", errors="ignore")
            saved_profiles = []
            for line in profile_output.split("\n"):
                if "All User Profile" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        profile = parts[1].strip()
                        if profile: saved_profiles.append(profile)

            # Format Output
            response = []
            if visible_networks:
                response.append(f"Visible Networks ({len(visible_networks)}): {', '.join(visible_networks)}")
            else:
                response.append("No visible networks found.")
                
            if saved_profiles:
                response.append(f"Saved Profiles ({len(saved_profiles)}): {', '.join(saved_profiles)}")
            else:
                response.append("No saved profiles found.")
                
            return "\n".join(response)

        except Exception as e:
            return f"Could not list networks: {e}"

    @staticmethod
    def _close_app(app_name):
        """Terminates a process by name."""
        app_name = app_name.lower()
        killed_count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name in proc.info['name'].lower():
                    proc.terminate()
                    killed_count += 1
            
            if killed_count > 0:
                return f"Terminated {killed_count} instance(s) of {app_name}."
            else:
                return f"No running process found matching '{app_name}'."
        except Exception as e:
            return f"Failed to close {app_name}: {e}"

    @staticmethod
    def run_diagnostics():
        """
        Performs a self-health check on system components (Diagnostics).
        """
        report = []
        status = "ONLINE"
        
        # 1. Internet Connectivity
        try:
             # Check Google DNS
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            report.append("Internet: CONNECTED")
        except:
             report.append("Internet: DISCONNECTED")
             status = "DEGRADED"

        # 2. Disk Space
        try:
            disk = psutil.disk_usage('/')
            free_gb = round(disk.free / (1024**3), 2)
            report.append(f"Disk Space: {free_gb} GB Free")
        except:
            report.append("Disk Check: FAILED")

        # 3. CPU/Memory
        try:
             cpu = psutil.cpu_percent(interval=0.1)
             memory = psutil.virtual_memory()
             total_ram = round(memory.total / (1024 ** 3), 2)
             used_ram = round(memory.used / (1024 ** 3), 2)
             report.append(f"CPU Load: {cpu}% | RAM Usage: {used_ram}GB / {total_ram}GB ({memory.percent}%)")
        except:
             report.append("System Monitor: FAILED")

        return f"System Status: {status}\n" + "\n".join(report)

    @staticmethod
    def _power_control(action):
        """Executes power commands: shutdown, restart, lock, sleep."""
        action = action.lower()
        try:
            if "shutdown" in action:
                os.system("shutdown /s /t 10")
                return "System will shut down in 10 seconds. Save your work."
            elif "restart" in action:
                os.system("shutdown /r /t 10")
                return "System will restart in 10 seconds."
            elif "lock" in action:
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "System locked."
            elif "sleep" in action:
                 os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                 return "Putting system to sleep."
            else:
                return f"Unknown power action: {action}"
        except Exception as e:
            return f"Power control failed: {e}"
