import speech_recognition as sr
import threading
import time
import os

class MeetingListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.transcript = []
        self.stop_listening_func = None

    def start_listening(self):
        """
        Starts listening in the background.
        """
        if self.is_listening:
            return "Already listening."

        self.is_listening = True
        self.transcript = []
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Start background listening
        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone, 
            self._callback
        )
        return "Meeting listener started. Speak naturally."

    def stop_listening(self):
        """
        Stops the background listener and saves the transcript.
        """
        if not self.is_listening:
            return "Not currently listening."

        self.is_listening = False
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None

        # Save transcript
        filename = f"meeting_notes_{int(time.time())}.txt"
        output_dir = os.path.join(os.getcwd(), "generated_docs")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "w") as f:
            f.write("\n".join(self.transcript))
        
        return f"Meeting notes saved to {filename}."

    def _callback(self, recognizer, audio):
        """
        Callback function called when audio is captured.
        """
        if not self.is_listening:
            return

        try:
            text = recognizer.recognize_google(audio)
            print(f"[Meeting Listener] Heard: {text}")
            self.transcript.append(text)
        except sr.UnknownValueError:
            # print("Google Speech Recognition could not understand audio")
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
