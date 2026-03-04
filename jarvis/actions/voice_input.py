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
        self.callback = callback_function
        self.is_running = False
        self.stop_listening_func = None
        self.paused = False

        # Awake state for continuous listening
        self.last_awake_time = 0
        self.awake_timeout = 15  # seconds to wait for follow-up without wake word

        # Use Windows default input (Microsoft Sound Mapper).
        # This always routes to whatever mic the user set as default in
        # Windows Sound Settings — no device-index guessing needed.
        self.microphone = sr.Microphone()
        print("[VoiceInput] Using system default microphone.")

    def start(self):
        """
        Starts the background listener.
        """
        if self.is_running:
            return

        print("[VoiceInput] Starting background listener...")
        self.is_running = True

        try:
            with self.microphone as source:
                print("[VoiceInput] Calibrating for ambient noise (1 sec)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                # Use a fixed low threshold so normal speech always triggers.
                # If ambient noise raises it above 300, clamp it back down.
                self.recognizer.energy_threshold = min(self.recognizer.energy_threshold, 300)
                # Disable dynamic adjustment — it can drift too high and silence the mic.
                self.recognizer.dynamic_energy_threshold = False
                self.recognizer.pause_threshold = 0.8
                print(f"[VoiceInput] energy_threshold={self.recognizer.energy_threshold:.1f} | Say 'Hey Jarvis...'")

        except Exception as e:
            print(f"[VoiceInput] Mic Error during calibration: {e}")
            self.is_running = False
            return

        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone,
            self._process_audio,
            phrase_time_limit=8
        )
        print("[VoiceInput] Background listener active.")

    def stop(self):
        """
        Stops the listener.
        """
        self.is_running = False
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None
        print("[VoiceInput] Listener stopped.")

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def _process_audio(self, recognizer, audio):
        """
        Called by listen_in_background whenever audio is captured above threshold.
        """
        if self.paused or not self.is_running:
            return

        print("[VoiceInput] Audio captured — sending to STT...", flush=True)

        try:
            text = recognizer.recognize_google(audio).lower()
            print(f"[VoiceInput] Heard: '{text}'", flush=True)

            # Wake Word Detection & Continuous Listening
            is_awake = (time.time() - self.last_awake_time) < self.awake_timeout

            if "jarvis" in text:
                self.last_awake_time = time.time()  # Wake up & reset timer
                pattern = r"(?:hey|hello|hi)?\s*jarvis\s*(.*)"
                match = re.search(pattern, text)
                if match:
                    command = match.group(1).strip()
                    if command:
                        print(f"[VoiceInput] Command extracted: '{command}'", flush=True)
                        self.callback(command)
                    else:
                        print("[VoiceInput] Wake word detected. Triggering greeting.", flush=True)
                        self.callback("hello")
            elif is_awake and len(text.strip()) > 2:
                # We are awake, accept this as a follow-up command
                self.last_awake_time = time.time()  # Reset timer to stay awake
                print(f"[VoiceInput] Follow-up command detected: '{text}'", flush=True)
                self.callback(text.strip())
            else:
                # Discard background chatter
                print(f"[VoiceInput] Ignored (Asleep/No wake word): '{text}'", flush=True)

        except sr.UnknownValueError:
            print("[VoiceInput] Could not understand audio.", flush=True)
        except sr.RequestError as e:
            print(f"[VoiceInput] Google STT API Error: {e}", flush=True)
        except Exception as e:
            print(f"[VoiceInput] Error: {e}", flush=True)
