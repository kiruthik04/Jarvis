import asyncio
import edge_tts
import pygame
import os
import threading
import queue
import time

class VoiceManager:
    def __init__(self):
        self.queue = queue.Queue()
        self.is_running = True
        self.current_process = None
        
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
        pygame.mixer.music.stop()

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
                
                # Generate Audio File
                output_file = "temp_speech.mp3"
                asyncio.run(self._generate_audio(text, output_file))
                
                # Play Audio
                self._play_audio(output_file)
                
                self.queue.task_done()
            except Exception as e:
                print(f"Voice Error: {e}")

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
        try:
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
            # Cleanup
            pass
            # os.remove(file_path) # Optional: keep for debug or delete

    def shutdown(self):
        self.is_running = False
        self.queue.put(None)
        pygame.mixer.quit()
