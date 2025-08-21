"""
Screen Capture Module
Handles screen capturing and remote input processing.
"""

import tkinter as tk
from PIL import Image, ImageGrab, ImageTk
import io
import json
import threading
import time
import base64

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

class ScreenCapture:
    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.compression_quality = 40  # Good balance for 200KB target
        self.scale_factor = 0.6  # Good resolution
        self.last_capture_time = 0
        self.min_frame_interval = 0.016  # 60+ FPS (1/60 = 0.016)
        
    def capture_screen(self):
        """Capture the current screen and return compressed image data"""
        try:
            # Rate limiting for 60+ FPS
            current_time = time.time()
            if current_time - self.last_capture_time < self.min_frame_interval:
                return None
            self.last_capture_time = current_time
            
            # Capture full screen
            screenshot = ImageGrab.grab()
            
            # Resize for better performance and smaller data
            new_width = int(screenshot.width * self.scale_factor)
            new_height = int(screenshot.height * self.scale_factor)
            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB to ensure proper JPEG encoding
            if screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')
            
            # Start with reasonable quality
            quality = self.compression_quality
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    # Create JPEG data
                    img_buffer = io.BytesIO()
                    screenshot.save(img_buffer, format='JPEG', quality=quality, optimize=True)
                    jpeg_data = img_buffer.getvalue()
                    img_buffer.close()
                    
                    # Check size - should be around 200KB or less
                    data_size = len(jpeg_data)
                    print(f"Image captured: {data_size} bytes ({data_size/1024:.1f}KB) at quality {quality}")
                    
                    # If too large, reduce quality
                    if data_size > 300000:  # 300KB max
                        quality = max(20, quality - 15)
                        if attempt < max_attempts - 1:
                            continue
                    
                    # Create the screen data packet with base64 encoded image
                    screen_data = {
                        'type': 'screen',
                        'width': new_width,
                        'height': new_height,
                        'data': base64.b64encode(jpeg_data).decode('ascii'),  # Base64 encode for JSON
                        'timestamp': current_time
                    }
                    
                    # Final safety check on the entire packet
                    test_json = json.dumps(screen_data, default=str)
                    if len(test_json) > 1000000:  # 1MB max for entire packet
                        print(f"Screen data packet too large: {len(test_json)} bytes, skipping")
                        return None
                    
                    return screen_data
                    
                except Exception as e:
                    print(f"JPEG creation error (attempt {attempt + 1}): {e}")
                    quality = max(20, quality - 10)
                    
            print("All compression attempts failed")
            return None
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
            
    def handle_remote_input(self, input_data):
        """Handle remote mouse and keyboard input"""
        try:
            if input_data['type'] == 'mouse_click':
                self._handle_mouse_click(input_data)
            elif input_data['type'] == 'mouse_move':
                self._handle_mouse_move(input_data)
            elif input_data['type'] == 'key_press':
                self._handle_key_press(input_data)
            elif input_data['type'] == 'scroll':
                self._handle_scroll(input_data)
                
        except Exception as e:
            print(f"Input handling error: {e}")
            
    def _handle_mouse_click(self, data):
        """Handle remote mouse click"""
        try:
            import pyautogui
            # Coordinates are already scaled by client
            x = data['x']
            y = data['y']
            
            if data['button'] == 'left':
                pyautogui.click(x, y)
            elif data['button'] == 'right':
                pyautogui.rightClick(x, y)
            elif data['button'] == 'double':
                pyautogui.doubleClick(x, y)
                
        except ImportError:
            print("PyAutoGUI not available for mouse control")
        except Exception as e:
            print(f"Mouse click error: {e}")
            
    def _handle_mouse_move(self, data):
        """Handle remote mouse movement"""
        try:
            import pyautogui
            # Coordinates are already scaled by client
            x = data['x']
            y = data['y']
            pyautogui.moveTo(x, y)
            
        except ImportError:
            print("PyAutoGUI not available for mouse control")
        except Exception as e:
            print(f"Mouse move error: {e}")
            
    def _handle_key_press(self, data):
        """Handle remote keyboard input"""
        try:
            import pyautogui
            
            key = data['key']
            if data['action'] == 'press':
                if len(key) == 1:
                    pyautogui.press(key)
                else:
                    # Special keys
                    if key == 'Enter':
                        pyautogui.press('enter')
                    elif key == 'Backspace':
                        pyautogui.press('backspace')
                    elif key == 'Tab':
                        pyautogui.press('tab')
                    elif key == 'Space':
                        pyautogui.press('space')
                    elif key.startswith('Ctrl+'):
                        combo_key = key.split('+')[1].lower()
                        pyautogui.hotkey('ctrl', combo_key)
                    elif key.startswith('Alt+'):
                        combo_key = key.split('+')[1].lower()
                        pyautogui.hotkey('alt', combo_key)
                        
        except ImportError:
            print("PyAutoGUI not available for keyboard control")
        except Exception as e:
            print(f"Key press error: {e}")
            
    def _handle_scroll(self, data):
        """Handle remote scroll input"""
        try:
            import pyautogui
            # Coordinates are already scaled by client
            x = data['x']
            y = data['y']
            pyautogui.scroll(data['clicks'], x, y)
            
        except ImportError:
            print("PyAutoGUI not available for scroll control")
        except Exception as e:
            print(f"Scroll error: {e}")


class RemoteViewer:
    """Remote desktop viewer window"""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.viewer_window = None
        self.canvas = None
        self.current_image = None
        
    def create_viewer_window(self):
        """Create the remote desktop viewer window"""
        self.viewer_window = tk.Toplevel()
        self.viewer_window.title("Remote Desktop Viewer")
        self.viewer_window.geometry("1024x768")
        self.viewer_window.configure(bg='black')
        
        # Create canvas for displaying remote desktop
        self.canvas = tk.Canvas(self.viewer_window, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse and keyboard events
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        
        self.viewer_window.bind("<Key>", self._on_key_press)
        self.viewer_window.focus_set()
        
        # Handle window close
        self.viewer_window.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def update_display(self, screen_data):
        """Update the viewer with new screen data"""
        try:
            if not self.viewer_window or not self.canvas:
                return
                
            # Decode base64 image data
            image_data = base64.b64decode(screen_data['data'])
            
            # Create image from data
            image = Image.open(io.BytesIO(image_data))
            
            # Update canvas to get current size
            self.canvas.update_idletasks()
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Use default size if canvas not yet rendered
            if canvas_width <= 1:
                canvas_width = 1024
            if canvas_height <= 1:
                canvas_height = 768
                
            # Calculate scaling to fit while maintaining aspect ratio
            img_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                # Image is wider, scale by width
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                # Image is taller, scale by height
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)
                
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            
            # Keep reference to prevent garbage collection
            self.current_image = photo
                
        except Exception as e:
            print(f"Display update error: {e}")
            
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
        # Scale coordinates from viewer to actual screen size
        scale_factor = 0.6  # This should match the server's scale_factor
        actual_x = int(event.x / scale_factor)
        actual_y = int(event.y / scale_factor)
        
        input_data = {
            'type': 'mouse_move',
            'x': actual_x,
            'y': actual_y
        }
        self._send_input(input_data)
        
    def _on_scroll(self, event):
        """Handle mouse scroll"""
        # Scale coordinates from viewer to actual screen size
        scale_factor = 0.6  # This should match the server's scale_factor
        actual_x = int(event.x / scale_factor)
        actual_y = int(event.y / scale_factor)
        
        input_data = {
            'type': 'scroll',
            'x': actual_x,
            'y': actual_y,
            'clicks': event.delta // 120  # Windows scroll units
        }
        self._send_input(input_data)
        
    def _on_key_press(self, event):
        """Handle key press"""
        key = event.keysym
        input_data = {
            'type': 'key_press',
            'key': key,
            'action': 'press'
        }
        self._send_input(input_data)
        
    def _send_mouse_event(self, button, x, y):
        """Send mouse event to server"""
        # Scale coordinates from viewer to actual screen size
        scale_factor = 0.6  # This should match the server's scale_factor
        actual_x = int(x / scale_factor)
        actual_y = int(y / scale_factor)
        
        input_data = {
            'type': 'mouse_click',
            'button': button,
            'x': actual_x,
            'y': actual_y
        }
        self._send_input(input_data)
        
    def _send_input(self, input_data):
        """Send input data to server"""
        if hasattr(self.parent_app, 'client') and self.parent_app.client:
            self.parent_app.client.send_input(input_data)
            
    def _on_close(self):
        """Handle viewer window close"""
        if self.parent_app:
            self.parent_app.disconnect_from_server()
        self.close()
        
    def close(self):
        """Close the viewer window"""
        if self.viewer_window:
            try:
                self.viewer_window.destroy()
            except:
                pass
            self.viewer_window = None
