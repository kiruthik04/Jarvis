import customtkinter as ctk
from src.ui.animation import ListeningIndicator
import tkinter as tk

class OverlayWindow(ctk.CTkToplevel):
    def __init__(self, master, width=200, height=200, restore_callback=None):
        super().__init__(master)
        
        self.restore_callback = restore_callback

        
        self.width = width
        self.height = height
        
        # Remove Window Decorations (Borderless)
        self.overrideredirect(True)
        
        # Always on Top
        self.attributes('-topmost', True)
        
        # Transparent Background Logic
        # We pick a specific color to be transparent.
        # "black" or "#000001" is commonly used.
        self.transparent_color = "#000001"
        self.configure(fg_color=self.transparent_color)
        self.attributes('-transparentcolor', self.transparent_color)
        
        # Position: Bottom Center
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = screen_height - height - 100 # 100px from bottom
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add the Orb
        # The Orb needs to use the SAME transparent bg color
        self.orb = ListeningIndicator(self, width=width, height=height, bg_color=self.transparent_color)
        self.orb.pack(fill="both", expand=True)
        
        # Make the window click-through (optional, but good for overlays)
        # On Windows, this is complex via ctypes. For now, let's just keep it simple.
        
        # Bind Double Click to Restore
        if self.restore_callback:
            self.bind("<Double-Button-1>", self.on_double_click)
            self.orb.bind("<Double-Button-1>", self.on_double_click)

    def on_double_click(self, event):
        if self.restore_callback:
            self.restore_callback()
        
    def set_state(self, state):
        self.orb.set_state(state)
        
    def show(self):
        self.deiconify()
        
    def hide(self):
        self.withdraw()
