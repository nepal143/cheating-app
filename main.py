#!/usr/bin/env python3
"""
IgniteRemote Professional - VS Code Style UI
Clean, minimalistic, professional remote desktop solution
Based on working version with modern UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import time
import sys
import os
import base64
import requests
from datetime import datetime

# Import our modules
from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedRemoteViewer, OptimizedInputHandler

class IgniteRemotePro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IgniteRemote Professional")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # VS Code inspired color scheme
        self.colors = {
            'bg_primary': '#1e1e1e',       # VS Code dark background
            'bg_secondary': '#252526',     # Sidebar background
            'bg_tertiary': '#2d2d30',      # Panel background
            'accent_blue': '#007acc',      # VS Code blue
            'accent_green': '#4ec9b0',     # Success color
            'accent_orange': '#dcdcaa',    # Warning color
            'accent_red': '#f14c4c',       # Error color
            'text_primary': '#cccccc',     # Primary text
            'text_secondary': '#969696',   # Secondary text
            'text_muted': '#6a9955',       # Muted text (comments)
            'border': '#3e3e3e',          # Border color
            'button_bg': '#0e639c',        # Button background
            'button_hover': '#1177bb',     # Button hover
        }
        
        # Initialize variables first (before UI setup)
        self.relay_client = RelayClient()
        self.screen_capture = OptimizedScreenCapture()
        self.remote_viewer = None
        self.input_handler = None
        self.relay_connected = False
        self.relay_mode = None
        self.relay_session_id = None
        self.viewer_window = None
        
        # Initialize UI variables
        self.session_code_var = tk.StringVar()
        self.session_code_var.set("Not Active")
        self.host_status_var = tk.StringVar()
        self.host_status_var.set("Ready to host")
        self.client_status_var = tk.StringVar()
        self.client_status_var.set("Not connected")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the VS Code style UI"""
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Apply VS Code style
        self.apply_vs_code_style()
        
    def setup_styles(self):
        """Setup ttk styles for VS Code theme"""
        style = ttk.Style()
        
        # Configure main styles
        style.theme_use('clam')
        
        # Configure Notebook (tabs)
        style.configure('VSCode.TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('VSCode.TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'],
                       padding=[12, 8],
                       borderwidth=0)
        
        style.map('VSCode.TNotebook.Tab',
                 background=[('selected', self.colors['bg_primary']),
                           ('active', self.colors['bg_tertiary'])],
                 foreground=[('selected', self.colors['text_primary']),
                           ('active', self.colors['text_primary'])])
        
        # Configure buttons
        style.configure('VSCode.TButton',
                       background=self.colors['button_bg'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=[10, 6])
        
        style.map('VSCode.TButton',
                 background=[('active', self.colors['button_hover']),
                           ('pressed', self.colors['accent_blue'])])
        
        # Configure frames
        style.configure('VSCode.TFrame',
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        # Configure labels
        style.configure('VSCode.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'])
        
        style.configure('VSCode.Title.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 14, 'bold'))
        
        style.configure('VSCode.Subtitle.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 10))
        
        # Configure entries
        style.configure('VSCode.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
    def create_layout(self):
        """Create the main layout"""
        # Create activity bar (left sidebar)
        self.activity_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], width=60)
        self.activity_bar.pack(side='left', fill='y')
        self.activity_bar.pack_propagate(False)
        
        # Create main content area
        self.main_area = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_area.pack(side='left', fill='both', expand=True)
        
        # Create title bar
        self.title_bar = tk.Frame(self.main_area, bg=self.colors['bg_primary'], height=40)
        self.title_bar.pack(fill='x', pady=(0, 1))
        self.title_bar.pack_propagate(False)
        
        # Add title
        title_label = tk.Label(self.title_bar, 
                              text="IgniteRemote Professional", 
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(side='left', padx=20, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_area, style='VSCode.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create tabs
        self.create_host_tab()
        self.create_client_tab()
        
        # Activity bar buttons
        self.create_activity_buttons()
        
    def create_activity_buttons(self):
        """Create activity bar buttons"""
        # Host button
        self.host_btn = tk.Button(self.activity_bar,
                                 text="📡",
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 14),
                                 relief='flat',
                                 width=4,
                                 command=lambda: self.notebook.select(0))
        self.host_btn.pack(pady=10)
        
        # Client button
        self.client_btn = tk.Button(self.activity_bar,
                                   text="🖥️",
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   font=('Segoe UI', 14),
                                   relief='flat',
                                   width=4,
                                   command=lambda: self.notebook.select(1))
        self.client_btn.pack(pady=5)
        
    def create_host_tab(self):
        """Create the host tab"""
        host_frame = ttk.Frame(self.notebook, style='VSCode.TFrame')
        self.notebook.add(host_frame, text="🟢 Host (Server)")
        
        # Header
        header_frame = ttk.Frame(host_frame, style='VSCode.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = ttk.Label(header_frame, text="Share Your Desktop", style='VSCode.Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, text="Allow others to view and control your screen", style='VSCode.Subtitle.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Session info
        session_frame = ttk.Frame(host_frame, style='VSCode.TFrame')
        session_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        session_label = ttk.Label(session_frame, text="Session Code:", style='VSCode.TLabel')
        session_label.pack(anchor='w')
        
        code_frame = ttk.Frame(session_frame, style='VSCode.TFrame')
        code_frame.pack(fill='x', pady=(5, 0))
        
        self.session_display = tk.Label(code_frame,
                                       textvariable=self.session_code_var,
                                       bg=self.colors['bg_tertiary'],
                                       fg=self.colors['accent_green'],
                                       font=('Courier New', 16, 'bold'),
                                       relief='solid',
                                       borderwidth=1,
                                       pady=10)
        self.session_display.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.copy_btn = ttk.Button(code_frame, text="📋 Copy", style='VSCode.TButton',
                                  command=self.copy_session_code)
        self.copy_btn.pack(side='right')
        
        # Controls
        controls_frame = ttk.Frame(host_frame, style='VSCode.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.start_btn = ttk.Button(controls_frame, text="▶️ Start Server", style='VSCode.TButton',
                                   command=self.start_hosting)
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹️ Stop Server", style='VSCode.TButton',
                                  command=self.stop_hosting, state='disabled')
        self.stop_btn.pack(side='left')
        
        # Status
        status_frame = ttk.Frame(host_frame, style='VSCode.TFrame')
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        status_label = ttk.Label(status_frame, text="Status:", style='VSCode.TLabel')
        status_label.pack(anchor='w')
        
        self.host_status_label = ttk.Label(status_frame, textvariable=self.host_status_var, style='VSCode.TLabel')
        self.host_status_label.pack(anchor='w', pady=(5, 0))
        
        # Log
        log_frame = ttk.Frame(host_frame, style='VSCode.TFrame')
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        log_title = ttk.Label(log_frame, text="Server Log:", style='VSCode.TLabel')
        log_title.pack(anchor='w')
        
        self.host_log = scrolledtext.ScrolledText(log_frame, 
                                                 bg=self.colors['bg_tertiary'],
                                                 fg=self.colors['text_primary'],
                                                 insertbackground=self.colors['text_primary'],
                                                 selectbackground=self.colors['accent_blue'],
                                                 state='disabled',
                                                 font=('Consolas', 9))
        self.host_log.pack(fill='both', expand=True, pady=(5, 0))
        
    def create_client_tab(self):
        """Create the client tab"""
        client_frame = ttk.Frame(self.notebook, style='VSCode.TFrame')
        self.notebook.add(client_frame, text="🔵 Connect (Client)")
        
        # Header
        header_frame = ttk.Frame(client_frame, style='VSCode.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = ttk.Label(header_frame, text="Connect to Remote Desktop", style='VSCode.Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, text="Enter session code to connect to a remote computer", style='VSCode.Subtitle.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Connection form
        connect_frame = ttk.Frame(client_frame, style='VSCode.TFrame')
        connect_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        code_label = ttk.Label(connect_frame, text="Session Code:", style='VSCode.TLabel')
        code_label.pack(anchor='w')
        
        entry_frame = ttk.Frame(connect_frame, style='VSCode.TFrame')
        entry_frame.pack(fill='x', pady=(5, 0))
        
        self.session_entry = ttk.Entry(entry_frame, style='VSCode.TEntry', font=('Courier New', 12))
        self.session_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.session_entry.bind('<Return>', lambda e: self.connect_to_session())
        
        self.connect_btn = ttk.Button(entry_frame, text="🔗 Connect", style='VSCode.TButton',
                                     command=self.connect_to_session)
        self.connect_btn.pack(side='right')
        
        # Controls
        controls_frame = ttk.Frame(client_frame, style='VSCode.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.disconnect_btn = ttk.Button(controls_frame, text="❌ Disconnect", style='VSCode.TButton',
                                        command=self.disconnect_client, state='disabled')
        self.disconnect_btn.pack(side='left')
        
        # Status
        status_frame = ttk.Frame(client_frame, style='VSCode.TFrame')
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        status_label = ttk.Label(status_frame, text="Status:", style='VSCode.TLabel')
        status_label.pack(anchor='w')
        
        self.client_status_label = ttk.Label(status_frame, textvariable=self.client_status_var, style='VSCode.TLabel')
        self.client_status_label.pack(anchor='w', pady=(5, 0))
        
        # Log
        log_frame = ttk.Frame(client_frame, style='VSCode.TFrame')
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        log_title = ttk.Label(log_frame, text="Client Log:", style='VSCode.TLabel')
        log_title.pack(anchor='w')
        
        self.client_log = scrolledtext.ScrolledText(log_frame, 
                                                   bg=self.colors['bg_tertiary'],
                                                   fg=self.colors['text_primary'],
                                                   insertbackground=self.colors['text_primary'],
                                                   selectbackground=self.colors['accent_blue'],
                                                   state='disabled',
                                                   font=('Consolas', 9))
        self.client_log.pack(fill='both', expand=True, pady=(5, 0))
        
    def apply_vs_code_style(self):
        """Apply additional VS Code styling"""
        # Configure scrollbars
        for widget in [self.host_log, self.client_log]:
            # Configure scrollbar
            scrollbar = widget.vbar
            scrollbar.config(
                bg=self.colors['bg_secondary'],
                troughcolor=self.colors['bg_tertiary'],
                activebackground=self.colors['text_secondary'],
                highlightthickness=0,
                borderwidth=0
            )
            
    def setup_relay_callbacks(self):
        """Setup relay client callbacks - working version"""
        self.relay_client.on_screen_data = self.handle_relay_screen_data
        self.relay_client.on_input_data = self.handle_relay_input_data  
        self.relay_client.on_connection_change = self.handle_relay_connection_change
        
    # HOST METHODS
    def start_hosting(self):
        """Start hosting via relay server"""
        self.log_to_host("🔄 Creating cloud session...")
        self.host_status_var.set("Creating session...")
        self.start_btn.config(state="disabled")
        
        def host_thread():
            try:
                self.setup_relay_callbacks()
                
                # Create session
                session_id = self.relay_client.create_session()
                if not session_id:
                    self.log_to_host("❌ Failed to create session")
                    self.host_status_var.set("Failed to create session")
                    self.start_btn.config(state="normal")
                    return
                
                self.relay_session_id = session_id
                self.session_code_var.set(session_id)
                self.copy_btn.config(state="normal")
                
                # Connect as host
                if self.relay_client.connect_as_host():
                    self.relay_connected = True
                    self.relay_mode = 'host'
                    
                    self.log_to_host(f"✅ Session created: {session_id}")
                    self.host_status_var.set(f"Hosting session: {session_id}")
                    
                    # Update UI
                    self.root.after(0, lambda: self.update_host_ui(True))
                    
                    # Start screen capture
                    self.start_screen_capture()
                else:
                    self.log_to_host("❌ Failed to connect as host")
                    self.host_status_var.set("Failed to start hosting")
                    self.start_btn.config(state="normal")
                    
            except Exception as e:
                self.log_to_host(f"❌ Error: {e}")
                self.host_status_var.set(f"Error: {e}")
                self.start_btn.config(state="normal")
                
        threading.Thread(target=host_thread, daemon=True).start()
        
    def stop_hosting(self):
        """Stop hosting"""
        self.relay_connected = False
        self.relay_mode = None
        
        if self.relay_client:
            self.relay_client.disconnect()
            
        if self.screen_capture:
            self.screen_capture.stop_capture()
            
        self.session_code_var.set("Not Active")
        self.host_status_var.set("Ready to host")
        self.update_host_ui(False)
        self.log_to_host("⏹️ Stopped hosting")
        
    def update_host_ui(self, hosting):
        """Update host UI state"""
        if hosting:
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.copy_btn.config(state="disabled")
            
    def start_screen_capture(self):
        """Start screen capture and streaming"""
        def capture_loop():
            while self.relay_connected and self.relay_mode == 'host':
                try:
                    # Capture screen
                    screen_data = self.screen_capture.capture_screen()
                    
                    if screen_data and 'data' in screen_data:
                        # Convert to base64 for relay
                        jpeg_bytes = screen_data['data']
                        base64_data = base64.b64encode(jpeg_bytes).decode('utf-8')
                        
                        # Send via relay
                        self.relay_client.send_screen_data(base64_data)
                        
                    time.sleep(1/30)  # 30 FPS
                except Exception as e:
                    self.log_to_host(f"❌ Capture error: {e}")
                    break
                    
        threading.Thread(target=capture_loop, daemon=True).start()
        
    def copy_session_code(self):
        """Copy session code to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.session_code_var.get())
            self.log_to_host("📋 Session code copied to clipboard")
        except Exception as e:
            self.log_to_host(f"❌ Failed to copy: {e}")
            
    def log_to_host(self, message):
        """Add a message to the host log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.host_log.config(state="normal")
            self.host_log.insert(tk.END, formatted_message)
            self.host_log.see(tk.END)
            self.host_log.config(state="disabled")
            
        self.root.after(0, update_log)
        
    # CLIENT METHODS - WORKING VERSION
    def connect_to_session(self):
        """Connect as relay client - working version"""
        session_code = self.session_entry.get().strip().upper()
        if not session_code:
            messagebox.showerror("Error", "Please enter session code")
            return
            
        if len(session_code) != 6:
            messagebox.showerror("Error", "Session code must be 6 characters")
            return
        
        self.log_to_client(f"🔄 Connecting to session: {session_code}")
        self.client_status_var.set(f"Connecting to {session_code}...")
        self.connect_btn.config(state="disabled")
        
        def connect_thread():
            try:
                self.setup_relay_callbacks()
                
                if self.relay_client.connect_as_client(session_code):
                    self.relay_connected = True
                    self.relay_mode = 'client'
                    self.relay_session_id = session_code
                    
                    self.log_to_client(f"✅ Connected to session: {session_code}")
                    self.client_status_var.set(f"Connected to {session_code} - Receiving screen...")
                    
                    self.root.after(0, lambda: self.update_client_ui(True))
                    
                    # Open remote viewer for relay connection - KEY WORKING PART
                    self.root.after(0, self.open_remote_viewer)
                else:
                    self.log_to_client(f"❌ Failed to connect to {session_code}")
                    self.client_status_var.set("Connection failed")
                    self.connect_btn.config(state="normal")
                    
            except Exception as e:
                self.log_to_client(f"❌ Connection error: {e}")
                self.client_status_var.set(f"Error: {e}")
                self.connect_btn.config(state="normal")
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_client(self):
        """Disconnect relay client"""
        self.relay_connected = False
        self.relay_mode = None
        
        if self.relay_client:
            self.relay_client.disconnect()
            
        # Close remote viewer
        if hasattr(self, 'remote_viewer') and self.remote_viewer:
            if hasattr(self.remote_viewer, 'viewer_window') and self.remote_viewer.viewer_window:
                self.remote_viewer.viewer_window.destroy()
            self.remote_viewer = None
            
        self.client_status_var.set("Not connected")
        self.update_client_ui(False)
        self.log_to_client("❌ Disconnected")
        
    def update_client_ui(self, connected):
        """Update client UI state"""
        if connected:
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
        else:
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            
    def log_to_client(self, message):
        """Add a message to the client log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.client_log.config(state="normal")
            self.client_log.insert(tk.END, formatted_message)
            self.client_log.see(tk.END)
            self.client_log.config(state="disabled")
            
        self.root.after(0, update_log)
        
    # REMOTE VIEWER METHODS - WORKING VERSION
    def open_remote_viewer(self):
        """Open the remote desktop viewer window - working version"""
        def create_viewer():
            self.remote_viewer = OptimizedRemoteViewer(self)
            self.remote_viewer.create_viewer_window()
            
        # Create viewer in main thread
        self.root.after(0, create_viewer)
        self.log_to_client("🖥️ Remote desktop viewer opened")
        
    # RELAY CALLBACK METHODS - WORKING VERSION
    def handle_relay_screen_data(self, data):
        """Handle received screen data from relay - working version"""
        try:
            # Decode base64 data to get JPEG bytes
            jpeg_bytes = base64.b64decode(data)
            
            # Create screen info dict like the original capture format
            screen_info = {
                'type': 'screen',
                'data': jpeg_bytes,
                'timestamp': time.time()
            }
            
            # Update remote viewer if it exists
            if hasattr(self, 'remote_viewer') and self.remote_viewer:
                self.remote_viewer.update_display(screen_info)
            else:
                # Create remote viewer if it doesn't exist
                self.open_remote_viewer()
                if hasattr(self, 'remote_viewer') and self.remote_viewer:
                    self.remote_viewer.update_display(screen_info)
                    
        except Exception as e:
            self.log_to_client(f"❌ Screen data error: {e}")
            
    def handle_relay_input_data(self, data):
        """Handle received input data from relay"""
        try:
            if hasattr(self, 'input_handler') and self.input_handler:
                self.input_handler.handle_input(data)
        except Exception as e:
            self.log_to_host(f"❌ Input error: {e}")
            
    def handle_relay_connection_change(self, connected):
        """Handle relay connection changes"""
        if not connected:
            self.log_to_client("⚠️ Relay connection lost")
            self.log_to_host("⚠️ Relay connection lost")
            
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = IgniteRemotePro()
    app.run()
