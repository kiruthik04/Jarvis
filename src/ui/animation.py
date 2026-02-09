import customtkinter as ctk
import math
import time

class ListeningIndicator(ctk.CTkCanvas):
    def __init__(self, master, width=100, height=100, bg_color=None):
        super().__init__(master, width=width, height=height, highlightthickness=0)
        
        # Use master's bg color if not provided
        if bg_color is None:
            try:
                bg_color = master.cget("fg_color")
                # CTk returns ["light_color", "dark_color"] list/tuple sometimes
                if isinstance(bg_color, (list, tuple)):
                    bg_color = bg_color[1] if len(bg_color) > 1 else bg_color[0]
                
                # Canvas doesn't support 'transparent', fallback to app bg
                if bg_color == "transparent":
                    bg_color = "#1a1a1a" 
            except:
                bg_color = "#1a1a1a"
                
        self.configure(bg=bg_color)
        
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.max_radius = (min(width, height) // 2) - 5
        
        self.is_animating = False
        self.state = "IDLE" # IDLE, LISTENING, PROCESSING, SPEAKING
        self.animation_id = None
        self.phase = 0
        
        # Colors
        self.COLOR_IDLE = "#00e5ff" # Cyan
        self.COLOR_LISTENING = "#00ff00" # Green
        self.COLOR_PROCESSING = "#ffcc00" # Yellow
        self.COLOR_SPEAKING = "#ff5555" # Red/Pink
        
        self.draw_idle()

    def set_state(self, new_state):
        if self.state == new_state:
            return
            
        self.state = new_state
        self.phase = 0
        
        if not self.is_animating:
            self.start_animation()

    def start_animation(self):
        self.is_animating = True
        self.animate()

    def stop_animation(self):
        self.is_animating = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.delete("all")
        self.draw_idle()

    def draw_idle(self):
        self.delete("all")
        # Static Ring
        self.create_oval(
            self.center_x - 10, self.center_y - 10,
            self.center_x + 10, self.center_y + 10,
            outline=self.COLOR_IDLE, width=2
        )
        self.create_oval(
            self.center_x - 30, self.center_y - 30,
            self.center_x + 30, self.center_y + 30,
            outline=self.COLOR_IDLE, width=1, dash=(5, 5)
        )

    def animate(self):
        if not self.is_animating:
            return

        self.delete("all")
        self.phase += 0.2
        
        if self.state == "LISTENING":
            # Pulsing effect
            pulse = (math.sin(self.phase) + 1) / 2 # 0 to 1
            radius = 20 + (pulse * 15)
            
            # Core
            self.create_oval(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                fill=self.COLOR_LISTENING, outline=""
            )
            # Outer Ring
            self.create_oval(
                self.center_x - 40, self.center_y - 40,
                self.center_x + 40, self.center_y + 40,
                outline=self.COLOR_LISTENING, width=2
            )

        elif self.state == "PROCESSING":
            # Spinning Ring
            radius = 30
            angle = self.phase * 50
            
            self.create_arc(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                start=angle, extent=90, style="arc", outline=self.COLOR_PROCESSING, width=4
            )
            self.create_arc(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                start=angle+180, extent=90, style="arc", outline=self.COLOR_PROCESSING, width=4
            )
            # Center Dot
            self.create_oval(
                self.center_x - 5, self.center_y - 5,
                self.center_x + 5, self.center_y + 5,
                fill=self.COLOR_PROCESSING
            )

        elif self.state == "SPEAKING":
            # Waveform simulation (Random bars)
            import random
            bar_count = 5
            spacing = 10
            start_x = self.center_x - ((bar_count * spacing) / 2)
            
            for i in range(bar_count):
                height = random.randint(10, 40)
                x = start_x + (i * spacing)
                self.create_line(
                    x, self.center_y - height,
                    x, self.center_y + height,
                    fill=self.COLOR_SPEAKING, width=5, capstyle="round"
                )

        else: # IDLE fallback in loop
            self.draw_idle()
            if self.is_animating: # If supposed to be animating but idle, stop
                 self.stop_animation()
                 return

        self.animation_id = self.after(50, self.animate)
