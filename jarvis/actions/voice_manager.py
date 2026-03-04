import asyncio
import edge_tts
import pygame
import os
import threading
import queue
import time

class VoiceManager:
    def __init__(self, on_speech_complete=None):
        self.queue = queue.Queue()
        self.is_running = True
        self.current_process = None
        self.on_speech_complete = on_speech_complete
        
        # Initialize Pygame Mixer
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Audio Error: {e}")

        # Voice Settings
        # Edge-TTS Voices:
        # Male: en-US-GuyNeural, en-US-ChristopherNeural
        # Female: en-US-JennyNeural, en-US-AriaNeural
        self.voice = "en-US-ChristopherNeural" 
        self.rate = "+0%"
        self.pitch = "+0Hz"

        # Background Worker
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def speak(self, text, emotion="NEUTRAL"):
        """
        Adds text to the speech queue with emotion parameters.
        """
        self.queue.put((text, emotion))

    def stop(self):
        """
        Stops playback and clears queue.
        """
        with self.queue.mutex:
            self.queue.queue.clear()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def stop_speaking(self):
        """Public alias for stop() — stops current speech and clears queue."""
        self.stop()

    def _worker(self):
        """
        Process loop to generate and play audio.
        """
        while self.is_running:
            try:
                item = self.queue.get()
                if item is None: break
                
                text, emotion = item
                print(f"[Voice] Speaking ({emotion}): {text[:30]}...")
                
                # Adjust Voice Params based on Emotion
                self._apply_emotion(emotion)
                
                # Generate Audio File with unique name to prevent PermissionError
                import time
                os.makedirs("assets", exist_ok=True)
                output_file = f"assets/temp_speech_{int(time.time()*1000)}.mp3"
                asyncio.run(self._generate_audio(text, output_file))
                
                # Play Audio
                self._play_audio(output_file)
                
                # Notify completion
                if self.on_speech_complete:
                    self.on_speech_complete()
                
                self.queue.task_done()
            except Exception as e:
                print(f"Voice Error: {e}")
                if hasattr(self, 'on_speech_complete') and self.on_speech_complete:
                     self.on_speech_complete()

    def _apply_emotion(self, emotion):
        """
        Tweaks rate/pitch to simulate emotion.
        """
        emotion = emotion.upper()
        if emotion == "HAPPY":
            self.rate = "+10%"
            self.pitch = "+2Hz"
        elif emotion == "SAD":
            self.rate = "-10%"
            self.pitch = "-5Hz"
        elif emotion == "EXHAUSTED":
            self.rate = "-15%"
            self.pitch = "-2Hz"
        elif emotion == "MOTIVATED":
            self.rate = "+15%"
            self.pitch = "+5Hz"
        elif emotion == "ANGRY":
             self.rate = "+5%"
             self.pitch = "+0Hz" 
        else: # NEUTRAL
            self.rate = "+0%"
            self.pitch = "+0Hz"

    async def _generate_audio(self, text, output_file):
        """
        Calls edge-tts to save mp3.
        """
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(output_file)

    def _play_audio(self, file_path):
        """
        Plays the audio file using pygame.
        """
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
            print(f"[Voice] Skipping playback: file invalid or too small — {file_path}")
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if not self.is_running:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"Playback Error: {e}")
        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass

    def shutdown(self):
        self.is_running = False
        self.stop() # make sure audio stops
        self.queue.put(None)
        
        # Wait for worker thread to finish its loop before quitting Pygame
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=3.0)
            except Exception:
                pass
                
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass
