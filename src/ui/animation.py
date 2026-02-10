import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter
import math
import time
import random

class ListeningIndicator(ctk.CTkLabel):
    def __init__(self, master, width=100, height=100, bg_color=None):
        super().__init__(master, text="", width=width, height=height)
        
        # Determine BG color
        if bg_color is None:
            try:
                bg_color = master.cget("fg_color")
                if isinstance(bg_color, (list, tuple)):
                    bg_color = bg_color[1] if len(bg_color) > 1 else bg_color[0]
                if bg_color == "transparent":
                    bg_color = "#1a1a1a"
            except:
                bg_color = "#1a1a1a"

        self.bg_color_hex = bg_color
        # Convert hex to RGB tuple for PIL
        self.bg_color_rgb = self.hex_to_rgb(bg_color)

        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        self.is_animating = False
        self.state = "IDLE" 
        self.animation_id = None
        self.start_time = time.time()
        
        # --- Pre-generate Blob Assets (Brushes) ---
        # We use a white radial gradient as a base 'brush'
        # Then we tint it on the fly
        self.brush_size = int(min(width, height) * 0.8)
        self.brush = self.create_radial_gradient_brush(self.brush_size)
        
        # Blob definitions: (x_offset, y_offset, scale, color_rgb, speed_factor)
        self.blobs = []
        self.update_blobs_for_state()
        
        self.draw_frame()

    def hex_to_rgb(self, hex_color):
        try:
            if not hex_color.startswith("#"):
                # Handle common CTk colors or fallback
                # CTk often returns 'gray14' etc.
                if "gray" in hex_color:
                    # quick parse 'grayXX' -> #XX0000? No, grayXX in Tk is usually gray level
                    pass 
                # Just fallback to dark gray for safety if not hex
                return (26, 26, 26) 
                
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = hex_color * 2
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
             return (26, 26, 26) # Default dark gray
        
    def create_radial_gradient_brush(self, size):
        # Create a grayscale image with radial falloff
        # Center = 255 (Opaque), Edge = 0 (Transparent)
        image = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(image)
        
        center = size // 2
        radius = size // 2
        
        # Draw concentric circles for gradient
        # (This is faster than per-pixel in pure python, though still O(N))
        # Better: calculate distance map? 
        # For simplicity and decent performance in initialization:
        for r in range(radius, 0, -1):
            alpha = int((1 - (r / radius))**2 * 255) # Quadratic falloff for smoother glow
            draw.ellipse((center - r, center - r, center + r, center + r), fill=alpha)
            
        return image

    def update_blobs_for_state(self):
        # Define blob configurations for each state
        # Colors are RGB tuples
        # Speeds are arbitrary multipliers
        
        t = time.time()
        
        if self.state == "IDLE":
            # Calm, Blue/Cyan, Slow
            self.blobs = [
                {"color": (0, 229, 255), "speed": 0.5, "phase": 0, "r_base": 0.6}, # Cyan
                {"color": (41, 121, 255), "speed": 0.7, "phase": 2, "r_base": 0.5}, # Blue
            ]
        elif self.state == "LISTENING":
            # Energetic, Green/Cyan, Pulsing
            self.blobs = [
                 {"color": (0, 255, 0),   "speed": 2.0, "phase": 0, "r_base": 0.7}, # Green
                 {"color": (0, 229, 255), "speed": 1.5, "phase": 1, "r_base": 0.6}, # Cyan
                 {"color": (170, 0, 255), "speed": 1.0, "phase": 3, "r_base": 0.5}, # Purple accent
            ]
        elif self.state == "PROCESSING":
            # Fast, Spinning, Yellow/Orange
             self.blobs = [
                 {"color": (255, 204, 0), "speed": 3.0, "phase": 0, "r_base": 0.6}, # Yellow
                 {"color": (255, 87, 34), "speed": 4.0, "phase": 2, "r_base": 0.5}, # Orange
             ]
        elif self.state == "SPEAKING":
            # Vibrating, Red/Pink/Purple
             self.blobs = [
                 {"color": (255, 85, 85),  "speed": 3.0, "phase": 0, "r_base": 0.6}, # Red
                 {"color": (255, 64, 129), "speed": 2.5, "phase": 1.5, "r_base": 0.6}, # Pink
                 {"color": (124, 77, 255), "speed": 2.0, "phase": 3.0, "r_base": 0.5}, # Purple
             ]

    def set_state(self, new_state):
        if self.state == new_state:
            return
            
        self.state = new_state
        self.update_blobs_for_state()
        
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
        # Could draw a static 'off' state here if needed
        
    def animate(self):
        if not self.is_animating:
            return
            
        self.draw_frame()
        # Schedule next frame (approx 30 FPS -> 33ms)
        self.animation_id = self.after(33, self.animate)

    def draw_frame(self):
        # Create base canvas (solid background color)
        # Using RGBA to allow layering
        base = Image.new("RGBA", (self.width, self.height), self.bg_color_rgb + (255,))
        
        t = time.time() - self.start_time
        
        # Composite blobs
        for b in self.blobs:
            # Calculate position based on noise/sine
            # Circular movement + noise
            speed = b["speed"]
            phase = b["phase"]
            
            # Orbit logic
            angle = (t * speed) + phase
            radius_variation = math.sin(t * speed * 1.5) * 10 
            orbit_radius = 10 + radius_variation
            
            cx = self.center_x + math.cos(angle) * orbit_radius
            cy = self.center_y + math.sin(angle) * orbit_radius
            
            # Scale logic (Pulsing)
            scale_pulse = (math.sin(t * speed * 2 + phase) + 1) / 4 # 0.0 to 0.5
            current_scale = b["r_base"] + (scale_pulse * 0.2)
            
            current_size = int(self.brush_size * current_scale)
            if current_size <= 0: continue
            
            # Resize brush (fast nearest neighbor is fine for glows, or bilinear)
            # Resizing every frame is expensive, but for <100px icons it's okay on modern CPU
            blob_img = self.brush.resize((current_size, current_size), resample=Image.Resampling.LANCZOS)
            
            # Colorize brush
            # Create a solid color image
            color_layer = Image.new("RGB", blob_img.size, b["color"])
            
            # Paste color using blob_img as mask
            # We paste onto a transparent layer first
            blob_layer = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
            
            paste_x = int(cx - current_size // 2)
            paste_y = int(cy - current_size // 2)
            
            # Create colored blob with alpha
            composite_blob = Image.new("RGBA", blob_img.size, b["color"] + (0,))
            composite_blob.paste(color_layer, (0,0), mask=blob_img)
            
            # Paste into layer
            blob_layer.paste(composite_blob, (paste_x, paste_y), mask=blob_img)
            
            # Additive blending simulation? 
            # Pillow alpha_composite merges layers standardly.
            # To get "glowing" look (Screen blend mode), it requires per-pixel math which is slow.
            # We will stick to standard alpha blending for performance.
            base = Image.alpha_composite(base, blob_layer)
            
        # Convert to CTkImage
        ctk_img = ctk.CTkImage(light_image=base, dark_image=base, size=(self.width, self.height))
        self.configure(image=ctk_img)
