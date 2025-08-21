#!/usr/bin/env python3
"""
SecureRemote Desktop Application
A legitimate remote desktop solution with system tray integration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import socket
import json
import time
import base64
import secrets
import hashlib
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import sys
import os

from screen_capture import ScreenCapture
from networking import SecureServer, SecureClient
from crypto_utils import CryptoManager

class RemoteDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SecureRemote Desktop")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Application state
        self.is_server_running = False
        self.is_client_connected = False
        self.server = None
        self.client = None
        self.connection_key = ""
        
        # System tray
        self.tray_icon = None
        self.is_hidden = False
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.crypto_manager = CryptoManager()
        
        self.setup_ui()
        self.setup_tray()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Server tab
        server_frame = ttk.Frame(notebook)
        notebook.add(server_frame, text="Host (Server)")
        self.setup_server_tab(server_frame)
        
        # Client tab
        client_frame = ttk.Frame(notebook)
        notebook.add(client_frame, text="Connect (Client)")
        self.setup_client_tab(client_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Choose Host or Connect mode")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")
        
        # Control buttons frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        
        # Hide button
        self.hide_btn = ttk.Button(controls_frame, text="Hide to Tray", command=self.hide_to_tray)
        self.hide_btn.pack(side="right", padx=(5, 0))
        
    def setup_server_tab(self, parent):
        """Setup the server/host tab"""
        # Info frame
        info_frame = ttk.LabelFrame(parent, text="Host Information", padding=10)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="When you start the server, a unique connection key will be generated.").pack(anchor="w")
        ttk.Label(info_frame, text="Share this key with the person who needs to connect to your desktop.").pack(anchor="w")
        
        # Connection key frame
        key_frame = ttk.LabelFrame(parent, text="Connection Key", padding=10)
        key_frame.pack(fill="x", padx=5, pady=5)
        
        self.key_display = tk.Text(key_frame, height=3, wrap="word", state="disabled", font=("Courier", 12))
        self.key_display.pack(fill="x")
        
        key_buttons_frame = ttk.Frame(key_frame)
        key_buttons_frame.pack(fill="x", pady=(5, 0))
        
        self.copy_key_btn = ttk.Button(key_buttons_frame, text="Copy Key", command=self.copy_key, state="disabled")
        self.copy_key_btn.pack(side="left")
        
        # Server controls
        controls_frame = ttk.LabelFrame(parent, text="Server Controls", padding=10)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_server_btn = ttk.Button(controls_frame, text="Start Server", command=self.start_server)
        self.start_server_btn.pack(side="left", padx=(0, 5))
        
        self.stop_server_btn = ttk.Button(controls_frame, text="Stop Server", command=self.stop_server, state="disabled")
        self.stop_server_btn.pack(side="left")
        
        # Connection log
        log_frame = ttk.LabelFrame(parent, text="Connection Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.server_log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.server_log.pack(fill="both", expand=True)
        
    def setup_client_tab(self, parent):
        """Setup the client/connect tab"""
        # Info frame
        info_frame = ttk.LabelFrame(parent, text="Connection Information", padding=10)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Enter the connection key provided by the host to connect.").pack(anchor="w")
        ttk.Label(info_frame, text="Make sure you have permission to access the remote desktop.").pack(anchor="w")
        
        # Connection key input
        input_frame = ttk.LabelFrame(parent, text="Enter Connection Key", padding=10)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        self.key_entry = tk.Text(input_frame, height=3, wrap="word", font=("Courier", 12))
        self.key_entry.pack(fill="x")
        
        # Client controls
        controls_frame = ttk.LabelFrame(parent, text="Connection Controls", padding=10)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        self.connect_btn = ttk.Button(controls_frame, text="Connect", command=self.connect_to_server)
        self.connect_btn.pack(side="left", padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(controls_frame, text="Disconnect", command=self.disconnect_from_server, state="disabled")
        self.disconnect_btn.pack(side="left")
        
        # Connection log
        log_frame = ttk.LabelFrame(parent, text="Connection Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.client_log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.client_log.pack(fill="both", expand=True)
        
    def setup_tray(self):
        """Setup system tray functionality"""
        # Create tray icon image
        image = Image.new('RGB', (64, 64), color='blue')
        
        # Create tray menu
        menu = pystray.Menu(
            item('Show', self.show_from_tray, default=True),
            item('Quit', self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("SecureRemote", image, "SecureRemote Desktop", menu)
        
    def hide_to_tray(self):
        """Hide the application to system tray"""
        self.root.withdraw()
        self.is_hidden = True
        
        # Start tray icon in separate thread
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
        
        self.log_to_server("Application minimized to system tray")
        
    def show_from_tray(self, icon=None, item=None):
        """Show the application from system tray"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_hidden = False
        
        if self.tray_icon:
            self.tray_icon.stop()
            
    def start_server(self):
        """Start the remote desktop server"""
        try:
            # Generate connection key
            self.connection_key = self.generate_connection_key()
            
            # Display key
            self.key_display.config(state="normal")
            self.key_display.delete(1.0, tk.END)
            self.key_display.insert(1.0, self.connection_key)
            self.key_display.config(state="disabled")
            
            # Update UI
            self.start_server_btn.config(state="disabled")
            self.stop_server_btn.config(state="normal")
            self.copy_key_btn.config(state="normal")
            
            # Start server
            self.server = SecureServer(self.crypto_manager)
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
            
            self.is_server_running = True
            self.status_var.set("Server running - Waiting for connections")
            self.log_to_server(f"Server started successfully")
            self.log_to_server(f"Connection key generated: {self.connection_key[:20]}...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.log_to_server(f"Error starting server: {str(e)}")
            
    def stop_server(self):
        """Stop the remote desktop server"""
        try:
            if self.server:
                self.server.stop()
                self.server = None
                
            self.is_server_running = False
            self.connection_key = ""
            
            # Update UI
            self.start_server_btn.config(state="normal")
            self.stop_server_btn.config(state="disabled")
            self.copy_key_btn.config(state="disabled")
            
            self.key_display.config(state="normal")
            self.key_display.delete(1.0, tk.END)
            self.key_display.config(state="disabled")
            
            self.status_var.set("Server stopped")
            self.log_to_server("Server stopped successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
            
    def connect_to_server(self):
        """Connect to a remote desktop server"""
        try:
            key = self.key_entry.get(1.0, tk.END).strip()
            if not key:
                messagebox.showwarning("Warning", "Please enter a connection key")
                return
                
            # Parse connection key to get server info
            server_info = self.parse_connection_key(key)
            if not server_info:
                messagebox.showerror("Error", "Invalid connection key")
                return
                
            # Update UI
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            # Start client
            self.client = SecureClient(self.crypto_manager)
            client_thread = threading.Thread(target=self.run_client, args=(server_info,), daemon=True)
            client_thread.start()
            
            self.is_client_connected = True
            self.status_var.set("Connecting to server...")
            self.log_to_client("Attempting to connect to server...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            self.log_to_client(f"Connection error: {str(e)}")
            
    def disconnect_from_server(self):
        """Disconnect from the remote desktop server"""
        try:
            if self.client:
                self.client.disconnect()
                self.client = None
                
            # Close remote viewer if open
            if hasattr(self, 'remote_viewer'):
                self.remote_viewer.close()
                delattr(self, 'remote_viewer')
                
            self.is_client_connected = False
            
            # Update UI
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            
            self.status_var.set("Disconnected from server")
            self.log_to_client("Disconnected successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {str(e)}")
            
    def generate_connection_key(self):
        """Generate a secure connection key"""
        # Generate random key components
        session_id = secrets.token_hex(16)
        server_ip = self.get_local_ip()
        server_port = 9999  # Default port
        timestamp = int(time.time())
        
        # Create key data
        key_data = {
            'session_id': session_id,
            'server_ip': server_ip,
            'server_port': server_port,
            'timestamp': timestamp,
            'version': '1.0'
        }
        
        # Encode key
        key_json = json.dumps(key_data)
        key_bytes = key_json.encode('utf-8')
        key_b64 = base64.b64encode(key_bytes).decode('utf-8')
        
        return key_b64
        
    def parse_connection_key(self, key):
        """Parse a connection key to extract server information"""
        try:
            key_bytes = base64.b64decode(key.encode('utf-8'))
            key_json = key_bytes.decode('utf-8')
            key_data = json.loads(key_json)
            
            # Validate key format
            required_fields = ['session_id', 'server_ip', 'server_port', 'timestamp']
            if not all(field in key_data for field in required_fields):
                return None
                
            # Check if key is not too old (24 hours)
            current_time = int(time.time())
            if current_time - key_data['timestamp'] > 86400:
                self.log_to_client("Warning: Connection key is more than 24 hours old")
                
            return key_data
            
        except Exception as e:
            self.log_to_client(f"Error parsing connection key: {str(e)}")
            return None
            
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
            
    def copy_key(self):
        """Copy connection key to clipboard"""
        if self.connection_key:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.connection_key)
            self.root.update()
            self.log_to_server("Connection key copied to clipboard")
            messagebox.showinfo("Success", "Connection key copied to clipboard!")
            
    def run_server(self):
        """Run the server in a separate thread"""
        try:
            self.server.start(port=9999)
            self.log_to_server("Server listening for connections...")
            
            while self.is_server_running:
                # Handle incoming connections
                if self.server.has_client():
                    self.log_to_server("Client connected successfully")
                    self.status_var.set("Client connected - Sharing desktop")
                    
                    # Start screen sharing
                    frame_count = 0
                    while self.server.is_connected() and self.is_server_running:
                        try:
                            # Capture screen
                            screen_data = self.screen_capture.capture_screen()
                            if screen_data:
                                success = self.server.send_screen_data(screen_data)
                                if success:
                                    frame_count += 1
                                    if frame_count % 30 == 0:  # Log every 30 frames (~1 second)
                                        self.log_to_server(f"Sent {frame_count} frames to client")
                                else:
                                    self.log_to_server("Failed to send screen data to client")
                            else:
                                self.log_to_server("Failed to capture screen")
                                
                            # Handle remote input
                            input_data = self.server.receive_input()
                            if input_data:
                                self.screen_capture.handle_remote_input(input_data)
                                
                            time.sleep(0.033)  # ~30 FPS
                            
                        except Exception as e:
                            self.log_to_server(f"Screen sharing error: {str(e)}")
                            break
                            
                    self.log_to_server("Client disconnected")
                    self.status_var.set("Server running - Waiting for connections")
                    
                time.sleep(0.1)
                
        except Exception as e:
            self.log_to_server(f"Server error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Server Error", str(e)))
            
    def run_client(self, server_info):
        """Run the client in a separate thread"""
        try:
            success = self.client.connect(server_info['server_ip'], server_info['server_port'])
            
            if success:
                self.log_to_client("Connected successfully to remote desktop")
                self.status_var.set("Connected - Receiving remote desktop")
                
                # Open remote desktop viewer window
                self.open_remote_viewer()
                
                # Give viewer time to open
                time.sleep(0.5)
                self.log_to_client("Starting screen data reception...")
                
                frame_count = 0
                while self.is_client_connected and self.client.is_connected():
                    try:
                        # Receive screen data
                        screen_data = self.client.receive_screen_data()
                        if screen_data:
                            self.update_remote_viewer(screen_data)
                            frame_count += 1
                            if frame_count % 30 == 0:  # Log every 30 frames (~1 second)
                                self.log_to_client(f"Received {frame_count} frames")
                        else:
                            # Log when no data received
                            if frame_count == 0:
                                self.log_to_client("Waiting for screen data from server...")
                            
                        time.sleep(0.033)  # ~30 FPS
                        
                    except Exception as e:
                        self.log_to_client(f"Connection error: {str(e)}")
                        break
                        
            else:
                self.log_to_client("Failed to connect to server")
                self.status_var.set("Connection failed")
                # Update UI on connection failure
                self.root.after(0, lambda: self.connect_btn.config(state="normal"))
                self.root.after(0, lambda: self.disconnect_btn.config(state="disabled"))
                
        except Exception as e:
            self.log_to_client(f"Client error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
            # Reset UI on error
            self.root.after(0, lambda: self.connect_btn.config(state="normal"))
            self.root.after(0, lambda: self.disconnect_btn.config(state="disabled"))
            
    def open_remote_viewer(self):
        """Open the remote desktop viewer window"""
        from screen_capture import RemoteViewer
        
        def create_viewer():
            self.remote_viewer = RemoteViewer(self)
            self.remote_viewer.create_viewer_window()
            
        # Create viewer in main thread
        self.root.after(0, create_viewer)
        self.log_to_client("Remote desktop viewer opened")
        
    def update_remote_viewer(self, screen_data):
        """Update the remote desktop viewer with new screen data"""
        if hasattr(self, 'remote_viewer') and self.remote_viewer.viewer_window:
            def update_display():
                self.remote_viewer.update_display(screen_data)
            self.root.after(0, update_display)
        
    def log_to_server(self, message):
        """Add a message to the server log"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.server_log.config(state="normal")
            self.server_log.insert(tk.END, formatted_message)
            self.server_log.see(tk.END)
            self.server_log.config(state="disabled")
            
        self.root.after(0, update_log)
        
    def log_to_client(self, message):
        """Add a message to the client log"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.client_log.config(state="normal")
            self.client_log.insert(tk.END, formatted_message)
            self.client_log.see(tk.END)
            self.client_log.config(state="disabled")
            
        self.root.after(0, update_log)
        
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.quit_application()
            
    def quit_application(self, icon=None, item=None):
        """Quit the application completely"""
        # Stop server if running
        if self.is_server_running:
            self.stop_server()
            
        # Disconnect client if connected
        if self.is_client_connected:
            self.disconnect_from_server()
            
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
            
        # Close application
        self.root.quit()
        sys.exit(0)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = RemoteDesktopApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")
