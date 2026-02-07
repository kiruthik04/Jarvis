import customtkinter as ctk
import threading
from src.brain.classifier import TaskClassifier
from src.brain.llm import ReasoningBrain
from src.actions.system_ops import SystemOps
from src.actions.browser import BrowserManager
from src.actions.voice import VoiceEngine

# --- THEME CONFIGURATION ---
COLOR_BG = "#1a1a1a"         # Dark Gray Background
COLOR_ACCENT = "#00e5ff"     # Cyan Accent
COLOR_TEXT = "#ffffff"       # White Text
COLOR_CHAT_BG = "#2b2b2b"    # Slightly lighter gray for chat
COLOR_INPUT_BG = "#333333"   # Input field background

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue") # Base theme

class JarvisUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S.")
        self.geometry("900x700")
        self.configure(fg_color=COLOR_BG)

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Chat area grows
        self.grid_rowconfigure(2, weight=0) # Input area fixed

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="J.A.R.V.I.S. SYSTEM ONLINE", 
            font=("Roboto Medium", 20), 
            text_color=COLOR_ACCENT
        )
        self.title_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.header_frame, 
            text="IDLE", 
            font=("Roboto", 12), 
            text_color="gray"
        )
        self.status_label.pack(side="right")

        # --- CHAT DISPLAY ---
        self.chat_display = ctk.CTkTextbox(
            self, 
            width=800, 
            height=500, 
            fg_color=COLOR_CHAT_BG,
            text_color=COLOR_TEXT,
            font=("Consolas", 14),
            corner_radius=10,
            border_width=1,
            border_color="#444444"
        )
        self.chat_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.chat_display.configure(state="disabled")

        # --- INPUT AREA ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_field = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Enter command...", 
            height=50, 
            font=("Roboto", 14),
            fg_color=COLOR_INPUT_BG,
            border_color="gray",
            border_width=1,
            corner_radius=20
        )
        self.input_field.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        self.input_field.bind("<Return>", self.on_enter_pressed)

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.btn_frame.grid(row=0, column=1, sticky="e")

        self.send_button = ctk.CTkButton(
            self.btn_frame, 
            text="SEND", 
            command=self.process_input, 
            height=45,
            width=100,
            corner_radius=20,
            fg_color=COLOR_ACCENT,
            hover_color="#00b8cc",
            text_color="black",
            font=("Roboto Bold", 14)
        )
        self.send_button.pack(side="left", padx=(0, 10))

        # Voice Toggle
        self.voice_enabled = ctk.BooleanVar(value=True)
        self.voice_toggle = ctk.CTkSwitch(
            self.btn_frame, 
            text="VOICE", 
            variable=self.voice_enabled, 
            onvalue=True, 
            offvalue=False,
            progress_color=COLOR_ACCENT,
            font=("Roboto", 12)
        )
        self.voice_toggle.pack(side="left")

        self.stop_audio_btn = ctk.CTkButton(
            self.btn_frame,
            text="STOP AUDIO",
            command=self.stop_audio,
            height=30,
            width=80,
            fg_color="#ff5555",
            hover_color="#cc0000",
            font=("Roboto Bold", 10)
        )
        self.stop_audio_btn.pack(side="left", padx=(10, 0))

        # --- INITIALIZATION ---
        self.log_to_chat("System", "Initializing Neural Interface...")
        self.update_idletasks()
        
        threading.Thread(target=self.initialize_backend, daemon=True).start()

    def update_status(self, text, color="gray"):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def initialize_backend(self):
        try:
            self.update_status("LOADING MODULES...", COLOR_ACCENT)
            self.classifier = TaskClassifier()
            self.brain = ReasoningBrain()
            self.voice = VoiceEngine()
            
            self.log_to_chat("System", "All systems nominal.")
            self.update_status("READY", "#00ff00") # Green
            
            if self.voice_enabled.get():
                self.voice.speak("Systems nominal. Ready for input.")
        except Exception as e:
            self.log_to_chat("Error", f"Initialization Failure: {e}")
            self.update_status("SYSTEM FAILURE", "red")

    def on_enter_pressed(self, event):
        self.process_input()
        
    def stop_audio(self):
        if hasattr(self, 'voice'):
            self.voice.stop_speaking()

    def log_to_chat(self, sender, message):
        self.after(0, lambda: self._log_to_chat_internal(sender, message))
        
    def _log_to_chat_internal(self, sender, message):
        self.chat_display.configure(state="normal")
        
        # Tags for coloring
        self.chat_display.tag_config("user", foreground=COLOR_ACCENT)
        self.chat_display.tag_config("jarvis", foreground="#ffffff") 
        self.chat_display.tag_config("system", foreground="#888888")
        self.chat_display.tag_config("error", foreground="#ff5555")

        if sender == "You":
            self.chat_display.insert("end", f"\n> You: {message}\n", "user")
        elif sender == "System":
             self.chat_display.insert("end", f"[SYSTEM]: {message}\n", "system")
        elif sender == "Error":
             self.chat_display.insert("end", f"[ERROR]: {message}\n", "error")
        else:
            self.chat_display.insert("end", f"\nJARVIS: {message}\n", "jarvis")
            # Speak all Jarvis responses if enabled
            if hasattr(self, 'voice') and self.voice and self.voice_enabled.get():
                self.voice.speak(message)
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def process_input(self):
        user_input = self.input_field.get()
        if not user_input.strip():
            return

        self.log_to_chat("You", user_input)
        self.input_field.delete(0, "end")
        self.input_field.configure(state="disabled")
        
        self.update_status("PROCESSING", COLOR_ACCENT)

        threading.Thread(target=self.run_pipeline, args=(user_input,), daemon=True).start()

    def run_pipeline(self, user_input):
        try:
            classification = self.classifier.classify(user_input)
            task_type = classification.get("task_type")
            
            if task_type == "SYSTEM_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                self.log_to_chat("System", f"Executing protocol: {intent}")
                result_message = SystemOps.execute_intent(intent, params)
                self.log_to_chat("Jarvis", result_message)

            elif task_type == "WEB_SEARCH":
                query = classification.get("query")
                self.log_to_chat("System", f"Searching network: {query}")
                BrowserManager().search_google(query)
                self.log_to_chat("Jarvis", "Search results displayed.")

            elif task_type == "THINK_AND_ANSWER":
                self.update_status("REASONING ENGINE ACTIVE", "#ffcc00") # Yellow
                self.log_to_chat("System", "Accessing neural pathways...")
                answer = self.brain.think(user_input)
                self.log_to_chat("Jarvis", answer)

            else:
                self.log_to_chat("Error", f"Unknown intent signature: {classification}")

        except Exception as e:
            self.log_to_chat("Error", str(e))
        finally:
             self.after(0, lambda: self.input_field.configure(state="normal"))
             self.after(0, lambda: self.input_field.focus())
             self.update_status("READY", "#00ff00")

if __name__ == "__main__":
    app = JarvisUI()
    app.mainloop()
