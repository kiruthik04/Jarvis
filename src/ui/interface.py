import customtkinter as ctk
import threading
from src.brain.classifier import TaskClassifier
from src.brain.llm import ReasoningBrain
from src.actions.system_ops import SystemOps
from src.actions.browser import BrowserManager
from src.actions.voice_manager import VoiceManager
from src.actions.office import OfficeAutomation
from src.actions.listener import MeetingListener
from src.actions.voice_input import VoiceInputListener
import os
from src.brain.agent import SystemAgent
from src.brain.memory import MemoryManager
from src.actions.automation import AutomationManager
from src.utils.logger import Logger
from src.ui.animation import ListeningIndicator
from src.ui.overlay import OverlayWindow
import time

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
        self.status_label.pack(side="right", padx=(10, 0))

        # floating Overlay (New)
        try:
            self.overlay = OverlayWindow(self, width=120, height=120)
            self.overlay.withdraw() # Start hidden until ready? Or show immediately?
            # Let's show it immediately so user sees it
            self.overlay.deiconify()
        except Exception as e:
            print(f"Overlay Error: {e}")
            self.overlay = None

        # Old Animation (Removed as per user request)
        # self.animation = ListeningIndicator(self.header_frame, width=40, height=40)
        # self.animation.pack(side="right")

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
        
        # Sync Animation (Overlay)
        state = "IDLE"
        if "LISTENING" in text:
            state = "LISTENING"
        elif "PROCESSING" in text or "REASONING" in text or "LOADING" in text:
             state = "PROCESSING"
        elif "READY" in text or "IDLE" in text:
             state = "IDLE"
             
        if self.overlay:
            # Only revert to IDLE if not currently speaking
            # (Speaking will revert itself after duration)
            if state == "IDLE" and self.overlay.orb.state == "SPEAKING":
                pass
            else:
                self.after(0, lambda: self.overlay.set_state(state))

    def initialize_backend(self):
        try:
            self.update_status("LOADING MODULES...", COLOR_ACCENT)
            self.classifier = TaskClassifier()
            self.brain = ReasoningBrain()
            self.browser = BrowserManager()
            self.voice = VoiceManager()
            self.listener = MeetingListener()
            self.agent = SystemAgent()
            self.memory = MemoryManager() # Persistent Memory
            self.logger = Logger() # Analytics
            self.automation = AutomationManager(callback_function=lambda msg: self.log_to_chat("Jarvis", msg))
            self.automation.start()
            
            # Voice Input (Wake Word)
            self.voice_input = VoiceInputListener(callback_function=self.on_voice_command)
            if self.voice_enabled.get():
                self.voice_input.start()

            self.log_to_chat("System", "All systems nominal. Office & Agent modules loaded.")
            
            if self.voice_enabled.get():
                self.update_status("LISTENING (HOTWORD)", "#00ff00") # Green
                self.voice.speak("Systems nominal. I am listening.")
            else:
                self.update_status("READY", "#00ff00")
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

        # Emotion Parsing
        emotion = "NEUTRAL"
        clean_message = message
        
        if "[EMOTION:" in message:
            import re
            match = re.search(r"\[EMOTION:\s*(\w+)\]", message)
            if match:
                emotion = match.group(1)
                clean_message = message.replace(match.group(0), "").strip()

        if sender == "You":
            self.chat_display.insert("end", f"\n> You: {clean_message}\n", "user")
        elif sender == "System":
             self.chat_display.insert("end", f"[SYSTEM]: {clean_message}\n", "system")
        elif sender == "Error":
             self.chat_display.insert("end", f"[ERROR]: {clean_message}\n", "error")
        else:
            self.chat_display.insert("end", f"\nJARVIS: {clean_message}\n", "jarvis")
            # Speak all Jarvis responses if enabled
            if hasattr(self, 'voice') and self.voice and self.voice_enabled.get():
                if self.overlay:
                     self.overlay.set_state("SPEAKING")
                
                # Voice is threaded...
                self.voice.speak(clean_message, emotion)
                
                # Estimate duration (very rough: 15 chars per sec?)
                duration_ms = max(2000, int(len(clean_message) / 15 * 1000))
                
                if self.overlay:
                    self.after(duration_ms, lambda: self.overlay.set_state("IDLE") if self.status_label.cget("text") == "READY" else None)
        
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

    def on_voice_command(self, command):
        """
        Callback for VoiceInputListener.
        """
        self.log_to_chat("You (Voice)", command)
        
        # Visual Feedback
        self.update_status("VOICE COMMAND RECEIVED", "#00e5ff")
        
        # Pause Listener (to avoid hearing self)
        if hasattr(self, 'voice_input'):
            self.voice_input.pause()
            
        threading.Thread(target=self.run_pipeline, args=(command,), daemon=True).start()

    def run_pipeline(self, user_input):
        start_time = time.time()
        classification = {}
        action_taken = "Unknown"
        response_text = ""
        
        try:
            # Contextual Handle: Open Last Generated File
            if hasattr(self, "last_generated_file") and self.last_generated_file:
                if user_input.lower().strip() in ["yes", "open it", "open", "sure", "ok", "please"]:
                    self.log_to_chat("System", f"Opening file: {self.last_generated_file}")
                    SystemOps._open_app(self.last_generated_file)
                    self.last_generated_file = None # Clear context
                    return

            classification = self.classifier.classify(user_input)
            task_type = classification.get("task_type")
            action_taken = task_type
            
            if task_type == "SYSTEM_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                self.log_to_chat("System", f"Executing protocol: {intent}")
                
                # Special Case for Diagnostics
                if intent == "system_status":
                     result_message = SystemOps.run_diagnostics()
                else:
                     result_message = SystemOps.execute_intent(intent, params)
                
                self.log_to_chat("Jarvis", result_message)
                response_text = result_message

            elif task_type == "OFFICE_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                topic = params.get("topic", "Untitled")
                content = params.get("content", "")
                
                self.log_to_chat("System", f"Office Protocol: {intent} - {topic}")
                
                result_path = None
                
                if intent == "create_word_document":
                    # Generate content if missing
                    if not content or len(content) < 10:
                        self.log_to_chat("System", "Generating content for document...")
                        content = self.brain.think(f"Generate content for a Word document about: {topic}")
                    
                    result_path = OfficeAutomation.create_word_document(topic, content)
                    
                elif intent == "create_presentation":
                    # Generate content for slides if missing
                    self.log_to_chat("System", "Generating slides content...")
                    raw_content = self.brain.think(f"Generate 3 slides content for a presentation about: {topic}. Format as 'Slide: Title \n Content'.")
                    
                    # Parse simplified content
                    slides = []
                    current_slide = {}
                    for line in raw_content.split('\n'):
                        if "Slide:" in line or "Title:" in line:
                            if current_slide: slides.append(current_slide)
                            current_slide = {'title': line.split(":")[-1].strip(), 'content': ''}
                        else:
                            if current_slide:
                                current_slide['content'] += line + "\n"
                    if current_slide: slides.append(current_slide)
                    
                    if not slides: # Fallback
                        slides = [{'title': topic, 'content': raw_content}]
                        
                    result_path = OfficeAutomation.create_presentation(topic, slides)

                # Handle Result
                if result_path and os.path.exists(result_path):
                    self.last_generated_file = result_path
                    self.log_to_chat("Jarvis", f"Document created successfully.\nLocation: {result_path}\n\nWould you like me to open it?")
                    response_text = f"Document created at {result_path}"
                else:
                    self.log_to_chat("Error", f"Failed to create document: {result_path}")
                    response_text = "Failed to create document"

            elif task_type == "MEETING_MODE":
                intent = classification.get("intent")
                if intent == "start_meeting":
                    msg = self.listener.start_listening()
                    self.log_to_chat("Jarvis", msg)
                    self.update_status("LISTENING (MEETING)", "#ff5555") # Red for recording
                    response_text = msg
                elif intent == "stop_meeting":
                    msg = self.listener.stop_listening()
                    self.log_to_chat("Jarvis", msg)
                    response_text = msg
            
            elif task_type == "MEMORY_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                key = params.get("key")
                value = params.get("value")
                
                if intent == "remember" and key and value:
                    msg = self.memory.remember(key, value)
                    self.log_to_chat("Jarvis", msg)
                    response_text = msg
                elif intent == "forget" and key:
                    msg = self.memory.forget(key)
                    self.log_to_chat("Jarvis", msg)
                    response_text = msg
                else:
                    self.log_to_chat("Jarvis", "I didn't catch what you wanted me to remember or forget.")
                    response_text = "Invalid memory request"

            elif task_type == "AUTOMATION_ACTION":
                intent = classification.get("intent")
                params = classification.get("parameters", {})
                
                if intent == "set_reminder":
                    msg = params.get("message")
                    time_str = params.get("time")
                    if msg and time_str:
                        res = self.automation.set_reminder(msg, time_str)
                        self.log_to_chat("Jarvis", res)
                        response_text = res
                    else:
                         self.log_to_chat("Jarvis", "I need both a message and time for the reminder.")
                         response_text = "Missing reminder params"
                
                elif intent == "list_reminders":
                    pending = self.automation.get_pending_reminders()
                    if pending:
                         self.log_to_chat("Jarvis", f"Pending Reminders: {pending}")
                         response_text = str(pending)
                    else:
                         self.log_to_chat("Jarvis", "No pending reminders.")
                         response_text = "No pending reminders"

            elif task_type == "GENERAL_TASK":
                goal = classification.get("goal")
                self.log_to_chat("System", f"Analyzing task: {goal}")
                
                # 1. Generate Code
                self.log_to_chat("System", "Generating execution plan...")
                code = self.brain.generate_code(goal)
                
                if code:
                    # 2. Execute Code
                    self.log_to_chat("System", "Executing agentic script...")
                    result = self.agent.run_generated_code(code)
                    self.log_to_chat("Jarvis", result)
                    response_text = result
                else:
                    self.log_to_chat("Jarvis", "I could not generate a plan for this task.")
                    response_text = "Code generation failed"

            elif task_type == "WEB_SEARCH":
                query = classification.get("query")
                self.log_to_chat("System", f"Searching network: {query}")
                
                # 1. Open Visual Browser (for user reference)
                self.browser.search_google(query)
                
                # 2. Extract & Summarize (Headless-ish)
                self.log_to_chat("System", "Analyzing search results...")
                url = self.browser.get_first_search_result(query)
                
                if url:
                    self.log_to_chat("System", f"Reading content from: {url}")
                    content = self.browser.extract_text(url)
                    
                    if content and len(content) > 100:
                        # 3. Summarize with LLM
                        self.log_to_chat("System", "Synthesizing information...")
                        summary_request = f"Summarize the following text in the context of the query '{query}':\n\n{content[:3000]}"
                        summary = self.brain.think(summary_request)
                        self.log_to_chat("Jarvis", f"Based on the top result:\n{summary}")
                        response_text = summary
                    else:
                        self.log_to_chat("Jarvis", "I found a result but couldn't extract readable content. Please check the browser.")
                        response_text = "Extraction failed"
                else:
                    self.log_to_chat("Jarvis", "I couldn't find a direct link to summarize, but I've opened the results for you.")
                    response_text = "No URL found"

            elif task_type == "THINK_AND_ANSWER":
                self.update_status("REASONING ENGINE ACTIVE", "#ffcc00") # Yellow
                self.log_to_chat("System", "Accessing neural pathways...")
                
                # Inject Memory Context
                mem_context = self.memory.get_all_context()
                answer = self.brain.think(user_input, memory_context=mem_context)
                self.log_to_chat("Jarvis", answer)
                response_text = answer

            else:
                self.log_to_chat("Error", f"Unknown intent signature: {classification}")
                response_text = "Unknown intent"
                
            # --- LOGGING ---
            if hasattr(self, 'logger'):
                latency = time.time() - start_time
                self.logger.log_interaction(user_input, classification, action_taken, response_text, latency)

        except Exception as e:
            self.log_to_chat("Error", f"Pipeline Error: {str(e)}")
            if hasattr(self, 'logger'):
                self.logger.log_error("Pipeline", str(e))
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()
        finally:
             if hasattr(self, 'listener') and not self.listener.is_listening:
                 self.update_status("READY", "#00ff00")
             
             # Resume Voice Listener
             if hasattr(self, 'voice_input') and self.voice_enabled.get():
                 self.voice_input.resume()
                 self.update_status("LISTENING (HOTWORD)", "#00ff00")

             self.after(0, lambda: self.input_field.configure(state="normal"))
             self.after(0, lambda: self.input_field.focus())

if __name__ == "__main__":
    app = JarvisUI()
    app.mainloop()
