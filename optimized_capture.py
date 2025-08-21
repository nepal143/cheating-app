"""
Optimized Screen Capture Module
A complete rewrite with proper compression and fast performance.
"""

import tkinter as tk
from PIL import Image, ImageGrab, ImageTk
import io
import time
import threading
import json

class OptimizedScreenCapture:
    def __init__(self):
        # Better quality settings while keeping data reasonable
        self.target_width = 960    # Higher resolution (720p-like)
        self.target_height = 720   # Much better quality
        self.jpeg_quality = 60     # Higher quality (was 40)
        self.max_fps = 60          # Keep high FPS for smooth mouse
        self.min_frame_interval = 1.0 / self.max_fps  # 60 FPS
        self.last_capture_time = 0
        self.max_data_size = 200000  # 200KB max per frame (reasonable for better quality)
        
    def capture_screen(self):
        """Capture screen with guaranteed small data size"""
        try:
            # Rate limiting for 60 FPS
            current_time = time.time()
            if current_time - self.last_capture_time < self.min_frame_interval:
                return None
            self.last_capture_time = current_time
            
            # Capture full screen
            screenshot = ImageGrab.grab()
            
            # Aggressively resize to fixed dimensions with high-quality scaling
            screenshot = screenshot.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
            
            # Ensure RGB mode
            if screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')
            
            # Try different quality levels until we get acceptable size
            for quality in [self.jpeg_quality, 50, 40, 30, 25]:  # Higher quality levels
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='JPEG', quality=quality, optimize=True)
                jpeg_data = img_buffer.getvalue()
                
                if len(jpeg_data) <= self.max_data_size:
                    print(f"Screen captured: {len(jpeg_data)} bytes ({len(jpeg_data)/1024:.1f}KB), quality={quality}, resolution={self.target_width}x{self.target_height}")
                    return {
                        'type': 'screen',
                        'width': self.target_width,
                        'height': self.target_height,
                        'data': jpeg_data,  # Raw JPEG bytes
                        'timestamp': current_time
                    }
            
            # If still too large, skip this frame
            print(f"Frame too large even at quality 10, skipping")
            return None
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None

class OptimizedRemoteViewer:
    def __init__(self, app):
        self.app = app
        self.viewer_window = None
        self.canvas = None
        self.current_image = None
        
    def create_viewer_window(self):
        """Create the remote desktop viewer window"""
        if self.viewer_window:
            return
            
        self.viewer_window = tk.Toplevel(self.app.root)
        self.viewer_window.title("Remote Desktop Viewer - High Quality")
        self.viewer_window.geometry("1200x900")  # Larger window for better quality
        
        # Canvas for displaying the remote screen
        self.canvas = tk.Canvas(self.viewer_window, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse event bindings
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        
        # Keyboard event bindings
        self.viewer_window.bind("<KeyPress>", self._on_key_press)
        self.viewer_window.focus_set()
        
        # Handle window close
        self.viewer_window.protocol("WM_DELETE_WINDOW", self.close)
        
    def update_display(self, screen_data):
        """Update the viewer with new screen data - OPTIMIZED"""
        try:
            if not self.viewer_window or not self.canvas:
                return
            
            # Get raw JPEG data
            jpeg_data = screen_data['data']
            
            # Create image directly from JPEG bytes
            image = Image.open(io.BytesIO(jpeg_data))
            
            # Get canvas dimensions
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 1200  # Better default size
            if canvas_height <= 1:
                canvas_height = 900
                
            # Resize image to fit canvas
            image = image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Clear canvas and display new image
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Keep reference to prevent garbage collection
            self.current_image = photo
            
        except Exception as e:
            print(f"Display update error: {e}")
            
    def close(self):
        """Close the viewer window"""
        if self.viewer_window:
            self.viewer_window.destroy()
            self.viewer_window = None
            self.canvas = None
            self.current_image = None
            
    def _on_left_click(self, event):
        """Handle left mouse click"""
        self._send_mouse_event('left', event.x, event.y)
        
    def _on_right_click(self, event):
        """Handle right mouse click"""
        self._send_mouse_event('right', event.x, event.y)
        
    def _on_double_click(self, event):
        """Handle double click"""
        self._send_mouse_event('double', event.x, event.y)
        
    def _on_mouse_move(self, event):
        """Handle mouse movement"""
        self._send_mouse_move(event.x, event.y)
        
    def _on_mouse_drag(self, event):
        """Handle mouse drag"""
        self._send_mouse_move(event.x, event.y)
        
    def _on_key_press(self, event):
        """Handle key press"""
        self._send_key_event(event.keysym)
        
    def _send_mouse_event(self, button, x, y):
        """Send mouse event to remote"""
        if hasattr(self.app, 'client') and self.app.client:
            # Scale coordinates from canvas to actual screen
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Get actual screen size from last frame
            actual_width = 1920  # Default, will be updated by screen data
            actual_height = 1080
            
            # Scale coordinates
            scaled_x = int(x * actual_width / canvas_width)
            scaled_y = int(y * actual_height / canvas_height)
            
            input_data = {
                'type': 'mouse_click',
                'button': button,
                'x': scaled_x,
                'y': scaled_y
            }
            
            # Send immediately for fast response
            threading.Thread(target=self.app.client.send_input, args=(input_data,), daemon=True).start()
            
    def _send_mouse_move(self, x, y):
        """Send mouse movement to remote"""
        if hasattr(self.app, 'client') and self.app.client:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            actual_width = 1920
            actual_height = 1080
            
            scaled_x = int(x * actual_width / canvas_width)
            scaled_y = int(y * actual_height / canvas_height)
            
            input_data = {
                'type': 'mouse_move',
                'x': scaled_x,
                'y': scaled_y
            }
            
            # Send immediately for fast response
            threading.Thread(target=self.app.client.send_input, args=(input_data,), daemon=True).start()
            
    def _send_key_event(self, key):
        """Send key event to remote"""
        if hasattr(self.app, 'client') and self.app.client:
            input_data = {
                'type': 'key_press',
                'key': key
            }
            
            threading.Thread(target=self.app.client.send_input, args=(input_data,), daemon=True).start()

class OptimizedInputHandler:
    def __init__(self):
        pass
        
    def handle_remote_input(self, input_data):
        """Handle remote mouse and keyboard input - FAST"""
        try:
            if input_data['type'] == 'mouse_click':
                self._handle_mouse_click(input_data)
            elif input_data['type'] == 'mouse_move':
                self._handle_mouse_move(input_data)
            elif input_data['type'] == 'key_press':
                self._handle_key_press(input_data)
        except Exception as e:
            print(f"Input handling error: {e}")
            
    def _handle_mouse_click(self, data):
        """Handle remote mouse click - INSTANT"""
        try:
            import pyautogui
            pyautogui.PAUSE = 0  # No pause for instant response
            x, y = data['x'], data['y']
            
            if data['button'] == 'left':
                pyautogui.click(x, y)
            elif data['button'] == 'right':
                pyautogui.rightClick(x, y)
            elif data['button'] == 'double':
                pyautogui.doubleClick(x, y)
                
        except ImportError:
            print("PyAutoGUI not available")
        except Exception as e:
            print(f"Mouse click error: {e}")
            
    def _handle_mouse_move(self, data):
        """Handle remote mouse movement - INSTANT"""
        try:
            import pyautogui
            pyautogui.PAUSE = 0  # No pause for instant response
            pyautogui.moveTo(data['x'], data['y'])
        except ImportError:
            print("PyAutoGUI not available")
        except Exception as e:
            print(f"Mouse move error: {e}")
            
    def _handle_key_press(self, data):
        """Handle remote key press"""
        try:
            import pyautogui
            pyautogui.PAUSE = 0
            pyautogui.press(data['key'])
        except ImportError:
            print("PyAutoGUI not available")
        except Exception as e:
            print(f"Key press error: {e}")
