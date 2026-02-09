import speech_recognition as sr
import threading
import time
import re

class VoiceInputListener:
    def __init__(self, callback_function):
        """
        :param callback_function: Function to call with the detected command text.
        """
        self.recognizer = sr.Recognizer()
        # Mic Selection
        mic_name = "default"
        try:
            mics = sr.Microphone.list_microphone_names()
            print(f"[VoiceInput] Available: {mics}")
            
            # Priority: 1. Microphone Array (Built-in), 2. USB/Headset, 3. Default
            array_indices = [i for i, name in enumerate(mics) if "Microphone Array" in name]
            other_indices = [i for i, name in enumerate(mics) if "USB" in name or "Headset" in name]
            
            if array_indices:
                device_index = array_indices[0]
                print(f"[VoiceInput] Selected: Microphone Array ({device_index})")
                self.microphone = sr.Microphone(device_index=device_index)
            elif other_indices:
                device_index = other_indices[0]
                print(f"[VoiceInput] Selected: Headset/USB ({device_index})")
                self.microphone = sr.Microphone(device_index=device_index)
            else:
                print("[VoiceInput] Using Default Mic")
                self.microphone = sr.Microphone()
                
            self._check_mic_health()
            
        except Exception as e:
            print(f"[VoiceInput] Error selecting mic: {e}")
            self.microphone = sr.Microphone()

        self.callback = callback_function 
        self.is_running = False
        self.stop_listening_func = None
        self.paused = False

    def _check_mic_health(self):
        """
        Briefly checks if the mic is receiving any signal.
        """
        print("[VoiceInput] Checking mic health...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # If energy threshold is very low, it might mean silence
                print(f"[VoiceInput] Energy Threshold: {self.recognizer.energy_threshold}")
                if self.recognizer.energy_threshold < 50:
                    print("[VoiceInput] WARNING: Mic signal is very weak or silent.")
        except Exception as e:
            print(f"[VoiceInput] Mic Health Check Failed: {e}")

    def start(self):
        """
        Starts the background listener.
        """
        if self.is_running: return

        print("[VoiceInput] Starting background listener...")
        self.is_running = True
        
        # Adjust for ambient noise
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.recognizer.dynamic_energy_threshold = True 
                self.recognizer.pause_threshold = 0.8
        except Exception as e:
            print(f"[VoiceInput] Mic Error: {e}")
            return

        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone, 
            self._process_audio
        )

    def stop(self):
        """
        Stops the listener.
        """
        self.is_running = False
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        # Re-adjust for noise if needed?
        # with self.microphone as source:
        #     self.recognizer.adjust_for_ambient_noise(source)

    def _process_audio(self, recognizer, audio):
        """
        Called when audio is captured.
        """
        if self.paused or not self.is_running:
            return

        try:
            # Use Google Web Speech API (Free, decent quality)
            text = recognizer.recognize_google(audio).lower()
            print(f"[VoiceInput] Heard: {text}")

            # Wake Word Detection
            # "Hey Jarvis", "Jarvis", "Hello Jarvis"
            if "jarvis" in text:
                # Extract command
                # "Hey Jarvis what time is it" -> "what time is it"
                pattern = r"(hey|hello|hi)?\s*jarvis\s*(.*)"
                match = re.search(pattern, text)
                
                if match:
                    command = match.group(2).strip()
                    if command:
                        print(f"[VoiceInput] Command: {command}")
                        self.callback(command)
                    else:
                        # Just "Jarvis?"
                        self.callback("Hello?") # Trigger greeting
        
        except sr.UnknownValueError:
            pass # No speech detected
        except sr.RequestError as e:
            print(f"[VoiceInput] API Error: {e}")
        except Exception as e:
            print(f"[VoiceInput] Error: {e}")
