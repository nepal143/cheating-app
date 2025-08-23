#!/usr/bin/env python3
"""
IgniteRemote Professional - VS Code Style UI
Clean, minimalistic, professional remote desktop solution
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import time
import sys
import os
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
        
        # Initialize UI variables that might be accessed from any tab
        self.session_code_var = tk.StringVar()
        self.session_code_var.set("Not Active")
        self.host_status_var = tk.StringVar()
        self.host_status_var.set("Ready to host")
        self.client_status_var = tk.StringVar()
        self.client_status_var.set("Not connected")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup VS Code style UI"""
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure ttk styles for VS Code look
        self.setup_styles()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True)
        
        # Title bar (VS Code style)
        self.create_title_bar(main_container)
        
        # Activity bar (left sidebar - VS Code style)
        self.create_activity_bar(main_container)
        
        # Main content area
        content_area = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_area.pack(side="left", fill="both", expand=True)
        
        # Tab bar
        self.create_tab_bar(content_area)
        
        # Content panels
        self.content_frame = tk.Frame(content_area, bg=self.colors['bg_primary'])
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Status bar at bottom
        self.create_status_bar(main_container)
        
        # Initialize with host tab
        self.current_tab = "host"
        self.show_host_panel()
        
    def setup_styles(self):
        """Setup VS Code inspired ttk styles"""
        style = ttk.Style()
        
        # Configure notebook (tabs)
        style.configure('VSCode.TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0,
                       tabmargins=0)
        
        style.configure('VSCode.TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'],
                       padding=[20, 8],
                       focuscolor='none',
                       borderwidth=0)
        
        style.map('VSCode.TNotebook.Tab',
                  background=[('selected', self.colors['bg_primary']),
                             ('active', self.colors['bg_tertiary'])],
                  foreground=[('selected', self.colors['text_primary'])])
    
    def create_title_bar(self, parent):
        """VS Code style title bar"""
        title_bar = tk.Frame(parent, bg=self.colors['bg_secondary'], height=35)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        
        # Left side - title
        left_frame = tk.Frame(title_bar, bg=self.colors['bg_secondary'])
        left_frame.pack(side="left", fill="y", padx=15)
        
        tk.Label(left_frame, text="IgniteRemote Professional", 
                font=("Segoe UI", 11), 
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(side="left", pady=8)
        
        # Right side - status
        right_frame = tk.Frame(title_bar, bg=self.colors['bg_secondary'])
        right_frame.pack(side="right", fill="y", padx=15)
        
        self.title_status_var = tk.StringVar()
        self.title_status_var.set("●  Ready")
        
        tk.Label(right_frame, textvariable=self.title_status_var, 
                font=("Segoe UI", 10), 
                bg=self.colors['bg_secondary'], fg=self.colors['accent_green']).pack(side="right", pady=8)
    
    def create_activity_bar(self, parent):
        """VS Code style activity bar (left sidebar)"""
        activity_bar = tk.Frame(parent, bg=self.colors['bg_secondary'], width=60)
        activity_bar.pack(side="left", fill="y")
        activity_bar.pack_propagate(False)
        
        # Host button
        self.host_btn = tk.Button(activity_bar, text="🖥️", 
                                 font=("Segoe UI", 20),
                                 bg=self.colors['bg_secondary'], fg=self.colors['accent_blue'],
                                 relief="flat", bd=0, width=3, height=2,
                                 command=lambda: self.switch_tab("host"),
                                 cursor="hand2")
        self.host_btn.pack(pady=10)
        
        # Client button  
        self.client_btn = tk.Button(activity_bar, text="🔗", 
                                   font=("Segoe UI", 20),
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                   relief="flat", bd=0, width=3, height=2,
                                   command=lambda: self.switch_tab("client"),
                                   cursor="hand2")
        self.client_btn.pack(pady=10)
        
        # Logs button
        self.logs_btn = tk.Button(activity_bar, text="📋", 
                                 font=("Segoe UI", 20),
                                 bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                 relief="flat", bd=0, width=3, height=2,
                                 command=lambda: self.switch_tab("logs"),
                                 cursor="hand2")
        self.logs_btn.pack(pady=10)
        
        # Settings button at bottom
        settings_frame = tk.Frame(activity_bar, bg=self.colors['bg_secondary'])
        settings_frame.pack(side="bottom", pady=20)
        
        tk.Button(settings_frame, text="⚙️", 
                 font=("Segoe UI", 18),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                 relief="flat", bd=0, width=3, height=2,
                 command=lambda: self.switch_tab("settings"),
                 cursor="hand2").pack()
    
    def create_tab_bar(self, parent):
        """VS Code style tab bar"""
        self.tab_bar = tk.Frame(parent, bg=self.colors['bg_secondary'], height=40)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)
        
        # Tab title
        self.tab_title_var = tk.StringVar()
        self.tab_title_var.set("Host Session")
        
        tk.Label(self.tab_bar, textvariable=self.tab_title_var, 
                font=("Segoe UI", 12, "bold"), 
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(side="left", padx=20, pady=10)
    
    def create_status_bar(self, parent):
        """VS Code style status bar"""
        status_bar = tk.Frame(parent, bg=self.colors['accent_blue'], height=25)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        # Left status
        left_status = tk.Frame(status_bar, bg=self.colors['accent_blue'])
        left_status.pack(side="left", fill="y", padx=10)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        tk.Label(left_status, textvariable=self.status_var, 
                font=("Segoe UI", 9), 
                bg=self.colors['accent_blue'], fg='white').pack(pady=3)
        
        # Right status
        right_status = tk.Frame(status_bar, bg=self.colors['accent_blue'])
        right_status.pack(side="right", fill="y", padx=10)
        
        tk.Label(right_status, text="IgniteRemote Pro v2.0", 
                font=("Segoe UI", 9), 
                bg=self.colors['accent_blue'], fg='white').pack(pady=3)
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        # Update activity bar button states
        self.host_btn.config(fg=self.colors['text_secondary'])
        self.client_btn.config(fg=self.colors['text_secondary'])
        self.logs_btn.config(fg=self.colors['text_secondary'])
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show selected tab
        if tab_name == "host":
            self.host_btn.config(fg=self.colors['accent_blue'])
            self.tab_title_var.set("Host Session")
            self.show_host_panel()
        elif tab_name == "client":
            self.client_btn.config(fg=self.colors['accent_blue'])
            self.tab_title_var.set("Join Session")
            self.show_client_panel()
        elif tab_name == "logs":
            self.logs_btn.config(fg=self.colors['accent_blue'])
            self.tab_title_var.set("Activity Logs")
            self.show_logs_panel()
        elif tab_name == "settings":
            self.tab_title_var.set("Settings")
            self.show_settings_panel()
        
        self.current_tab = tab_name
    
    def show_host_panel(self):
        """Show host panel with VS Code styling"""
        # Main container
        main_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_container, bg=self.colors['bg_primary'])
        header.pack(fill="x", pady=(0, 30))
        
        tk.Label(header, text="Share Your Desktop", 
                font=("Segoe UI", 24), 
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(side="left")
        
        # Description
        tk.Label(main_container, text="Allow others to remotely connect and control your computer", 
                font=("Segoe UI", 12), 
                bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack(anchor="w", pady=(0, 40))
        
        # Control panel
        control_panel = tk.Frame(main_container, bg=self.colors['bg_tertiary'], 
                                relief="flat", bd=1, padx=30, pady=30)
        control_panel.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(control_panel, bg=self.colors['bg_tertiary'])
        button_frame.pack(fill="x", pady=(0, 20))
        
        self.host_start_btn = tk.Button(button_frame, text="Start Hosting", 
                                       font=("Segoe UI", 12),
                                       bg=self.colors['button_bg'], fg='white',
                                       relief="flat", bd=0, padx=25, pady=10,
                                       command=self.start_hosting,
                                       cursor="hand2")
        self.host_start_btn.pack(side="left", padx=(0, 15))
        
        self.host_stop_btn = tk.Button(button_frame, text="Stop Hosting", 
                                      font=("Segoe UI", 12),
                                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                      relief="flat", bd=0, padx=25, pady=10,
                                      command=self.stop_hosting, state="disabled",
                                      cursor="hand2")
        self.host_stop_btn.pack(side="left")
        
        # Session code section
        code_section = tk.Frame(control_panel, bg=self.colors['bg_tertiary'])
        code_section.pack(fill="x", pady=(20, 0))
        
        tk.Label(code_section, text="Session Code", 
                font=("Segoe UI", 11, "bold"), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_primary']).pack(anchor="w", pady=(0, 10))
        
        code_display_frame = tk.Frame(code_section, bg=self.colors['bg_primary'], 
                                     relief="solid", bd=1, padx=20, pady=15)
        code_display_frame.pack(fill="x", pady=(0, 15))
        
        self.code_display = tk.Label(code_display_frame, textvariable=self.session_code_var, 
                                    font=("JetBrains Mono", 18, "bold"), 
                                    bg=self.colors['bg_primary'], fg=self.colors['accent_red'])
        self.code_display.pack()
        
        self.copy_code_btn = tk.Button(code_section, text="Copy to Clipboard", 
                                      font=("Segoe UI", 10),
                                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                      relief="flat", bd=0, padx=20, pady=8,
                                      command=self.copy_session_code, state="disabled",
                                      cursor="hand2")
        self.copy_code_btn.pack(anchor="w")
        
        # Status section
        status_section = tk.Frame(main_container, bg=self.colors['bg_tertiary'], 
                                 relief="flat", bd=1, padx=20, pady=15)
        status_section.pack(fill="x")
        
        tk.Label(status_section, text="Status", 
                font=("Segoe UI", 11, "bold"), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_primary']).pack(side="left")
        
        tk.Label(status_section, textvariable=self.host_status_var, 
                font=("Segoe UI", 10), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack(side="left", padx=(20, 0))
    
    def show_client_panel(self):
        """Show client panel with VS Code styling"""
        # Main container
        main_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_container, bg=self.colors['bg_primary'])
        header.pack(fill="x", pady=(0, 30))
        
        tk.Label(header, text="Connect to Remote Desktop", 
                font=("Segoe UI", 24), 
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(side="left")
        
        # Description
        tk.Label(main_container, text="Enter a session code to connect to and control another computer", 
                font=("Segoe UI", 12), 
                bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack(anchor="w", pady=(0, 40))
        
        # Connection panel
        connection_panel = tk.Frame(main_container, bg=self.colors['bg_tertiary'], 
                                   relief="flat", bd=1, padx=30, pady=30)
        connection_panel.pack(fill="x", pady=(0, 20))
        
        # Input section
        input_section = tk.Frame(connection_panel, bg=self.colors['bg_tertiary'])
        input_section.pack(fill="x", pady=(0, 20))
        
        tk.Label(input_section, text="Session Code", 
                font=("Segoe UI", 11, "bold"), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_primary']).pack(anchor="w", pady=(0, 10))
        
        self.code_entry = tk.Entry(input_section, font=("JetBrains Mono", 14), 
                                  width=15, bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                                  relief="solid", bd=1, insertbackground=self.colors['text_primary'])
        self.code_entry.pack(anchor="w", ipady=8)
        self.code_entry.bind('<Return>', lambda e: self.connect_to_session())
        
        # Buttons
        button_frame = tk.Frame(connection_panel, bg=self.colors['bg_tertiary'])
        button_frame.pack(fill="x", pady=(20, 0))
        
        self.client_connect_btn = tk.Button(button_frame, text="Connect", 
                                           font=("Segoe UI", 12),
                                           bg=self.colors['button_bg'], fg='white',
                                           relief="flat", bd=0, padx=25, pady=10,
                                           command=self.connect_to_session,
                                           cursor="hand2")
        self.client_connect_btn.pack(side="left", padx=(0, 15))
        
        self.client_disconnect_btn = tk.Button(button_frame, text="Disconnect", 
                                              font=("Segoe UI", 12),
                                              bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                              relief="flat", bd=0, padx=25, pady=10,
                                              command=self.disconnect_from_session, state="disabled",
                                              cursor="hand2")
        self.client_disconnect_btn.pack(side="left")
        
        # Status section
        status_section = tk.Frame(main_container, bg=self.colors['bg_tertiary'], 
                                 relief="flat", bd=1, padx=20, pady=15)
        status_section.pack(fill="x")
        
        tk.Label(status_section, text="Connection Status", 
                font=("Segoe UI", 11, "bold"), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_primary']).pack(side="left")
        
        tk.Label(status_section, textvariable=self.client_status_var, 
                font=("Segoe UI", 10), 
                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary']).pack(side="left", padx=(20, 0))
    
    def show_logs_panel(self):
        """Show logs panel with VS Code styling"""
        # Main container
        main_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Log display
        self.activity_log = scrolledtext.ScrolledText(main_container,
                                                     bg=self.colors['bg_primary'], 
                                                     fg=self.colors['text_primary'],
                                                     font=("JetBrains Mono", 10),
                                                     relief="flat", bd=0,
                                                     insertbackground=self.colors['text_primary'],
                                                     selectbackground=self.colors['bg_secondary'])
        self.activity_log.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure text tags for colored output
        self.activity_log.tag_config("info", foreground=self.colors['text_primary'])
        self.activity_log.tag_config("success", foreground=self.colors['accent_green'])
        self.activity_log.tag_config("warning", foreground=self.colors['accent_orange'])
        self.activity_log.tag_config("error", foreground=self.colors['accent_red'])
        self.activity_log.tag_config("timestamp", foreground=self.colors['text_muted'])
    
    def show_settings_panel(self):
        """Show settings panel"""
        main_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(main_container, text="Settings", 
                font=("Segoe UI", 24), 
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(anchor="w", pady=(0, 30))
        
        tk.Label(main_container, text="Settings panel - coming soon", 
                font=("Segoe UI", 12), 
                bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack(anchor="w")
    
    def update_code_display_color(self, state):
        """Safely update code display color"""
        try:
            if hasattr(self, 'code_display'):
                if state == 'success':
                    self.code_display.config(fg=self.colors['accent_green'])
                else:
                    self.code_display.config(fg=self.colors['accent_red'])
        except:
            pass
    
    def update_copy_button(self, enabled):
        """Safely update copy button state"""
        try:
            if hasattr(self, 'copy_code_btn'):
                if enabled:
                    self.copy_code_btn.config(state="normal", bg=self.colors['button_bg'], fg='white')
                else:
                    self.copy_code_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        except:
            pass
    
    def update_host_buttons(self, state):
        """Safely update host button states"""
        try:
            if hasattr(self, 'host_start_btn') and hasattr(self, 'host_stop_btn'):
                if state == 'active':
                    self.host_start_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
                    self.host_stop_btn.config(state="normal", bg=self.colors['accent_red'], fg='white')
                else:
                    self.host_start_btn.config(state="normal", bg=self.colors['button_bg'], fg='white')
                    self.host_stop_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        except:
            pass
    
    # Event handlers
    def start_hosting(self):
        """Start hosting a session"""
        self.log_activity("Starting host session...", "info")
        self.title_status_var.set("●  Creating Session...")
        self.status_var.set("Creating session...")
        self.host_start_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        
        def host_thread():
            try:
                self.root.after(0, lambda: self.log_activity("Connecting to relay server...", "info"))
                
                # Create session
                session_id = self.relay_client.create_session()
                if session_id:
                    self.relay_session_id = session_id
                    self.root.after(0, lambda: self.log_activity(f"Session ID created: {session_id}", "success"))
                    
                    # Update UI on main thread
                    self.root.after(0, lambda: self.session_code_var.set(session_id))
                    self.root.after(0, lambda: self.update_code_display_color('success'))
                    self.root.after(0, lambda: self.update_copy_button(True))
                    self.root.after(0, lambda: self.update_host_buttons('active'))
                    self.root.after(0, lambda: self.title_status_var.set("●  Hosting Active"))
                    self.root.after(0, lambda: self.status_var.set(f"Hosting session: {session_id}"))
                    self.root.after(0, lambda: self.host_status_var.set(f"Hosting session {session_id}"))
                    self.root.after(0, lambda: self.log_activity(f"Session created: {session_id}", "success"))
                    
                    # Connect as host
                    self.root.after(0, lambda: self.log_activity("Establishing host connection...", "info"))
                    if self.relay_client.connect_as_host():
                        self.relay_connected = True
                        self.relay_mode = 'host'
                        self.root.after(0, lambda: self.log_activity("Host connected successfully", "success"))
                        self.root.after(0, lambda: self.log_activity("Ready to accept connections", "info"))
                        
                        # Start screen sharing thread
                        self.root.after(0, lambda: self.log_activity("Starting screen capture...", "info"))
                        self.start_screen_sharing()
                        
                    else:
                        self.root.after(0, lambda: self.log_activity("Failed to connect as host", "error"))
                        self.root.after(0, lambda: self.reset_host_ui())
                else:
                    self.root.after(0, lambda: self.log_activity("Failed to create session - check relay server", "error"))
                    self.root.after(0, lambda: self.reset_host_ui())
                    
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.log_activity("Cannot connect to relay server - check internet connection", "error"))
                self.root.after(0, lambda: self.reset_host_ui())
            except requests.exceptions.Timeout:
                self.root.after(0, lambda: self.log_activity("Relay server timeout - server may be sleeping, try again", "warning"))
                self.root.after(0, lambda: self.reset_host_ui())
            except Exception as e:
                self.root.after(0, lambda: self.log_activity(f"Error: {str(e)}", "error"))
                self.root.after(0, lambda: self.reset_host_ui())
                
        threading.Thread(target=host_thread, daemon=True).start()
        
    def start_screen_sharing(self):
        """Start the screen sharing loop for hosting"""
        def screen_sharing_loop():
            self.log_activity("🎥 Starting screen capture loop...", "info")
            last_capture_time = 0
            frame_time = 1.0 / 30  # 30 FPS for smooth performance
            
            while self.relay_connected and self.relay_mode == 'host':
                try:
                    current_time = time.time()
                    
                    # Only capture if enough time has passed (consistent timing)
                    if current_time - last_capture_time >= frame_time:
                        # Capture screen using optimized capture
                        screen_info = self.screen_capture.capture_screen()
                        
                        if screen_info and 'data' in screen_info:
                            # Send the JPEG data directly (it will be base64 encoded by relay_client)
                            if self.relay_client.send_screen_data(screen_info['data']):
                                last_capture_time = current_time
                            else:
                                self.root.after(0, lambda: self.log_activity("❌ Failed to send screen data", "warning"))
                                # Don't break immediately, try again
                        
                        # Reduced sleep to prevent CPU overload but maintain speed
                        time.sleep(0.005)  # 5ms
                    else:
                        # Much smaller sleep for better responsiveness
                        time.sleep(0.001)  # 1ms
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log_activity(f"Screen sharing error: {str(e)}", "error"))
                    break
                    
            self.root.after(0, lambda: self.log_activity("🛑 Screen sharing stopped", "info"))
            
        # Start screen sharing in separate thread
        threading.Thread(target=screen_sharing_loop, daemon=True).start()
        self.root.after(0, lambda: self.log_activity("🎬 Screen sharing thread started", "success"))
    
    def stop_hosting(self):
        """Stop hosting"""
        self.relay_connected = False
        self.relay_mode = None
        
        if self.relay_client:
            self.relay_client.disconnect()
        
        self.reset_host_ui()
        self.log_activity("Hosting stopped", "warning")
    
    def reset_host_ui(self):
        """Reset host UI to default state"""
        self.update_host_buttons('inactive')
        self.update_copy_button(False)
        self.session_code_var.set("Not Active")
        self.update_code_display_color('error')
        self.title_status_var.set("●  Ready")
        self.status_var.set("Ready")
        self.host_status_var.set("Ready to host")
    
    def connect_to_session(self):
        """Connect to a session"""
        session_code = self.code_entry.get().strip()
        if not session_code:
            self.log_activity("Please enter a session code", "warning")
            return
        
        self.log_activity(f"Connecting to session: {session_code}", "info")
        self.client_connect_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.title_status_var.set("●  Connecting...")
        self.status_var.set("Connecting...")
        self.client_status_var.set("Connecting...")
        
        def client_thread():
            try:
                # Connect as client to session
                self.root.after(0, lambda: self.log_activity(f"Joining session: {session_code}...", "info"))
                
                if self.relay_client.join_session(session_code):
                    self.root.after(0, lambda: self.log_activity("Connected to session", "success"))
                    
                    # Connect as client
                    if self.relay_client.connect_as_client():
                        self.relay_connected = True
                        self.relay_mode = 'client'
                        self.relay_session_id = session_code
                        
                        # Set up callbacks to receive screen data
                        self.relay_client.on_screen_data = self.on_screen_data_received
                        
                        self.root.after(0, lambda: self.log_activity("Client connected successfully", "success"))
                        self.root.after(0, lambda: self.client_disconnect_btn.config(state="normal", bg=self.colors['accent_red'], fg='white'))
                        self.root.after(0, lambda: self.code_entry.config(state="disabled"))
                        self.root.after(0, lambda: self.title_status_var.set("●  Connected"))
                        self.root.after(0, lambda: self.status_var.set(f"Connected to: {session_code}"))
                        self.root.after(0, lambda: self.client_status_var.set(f"Connected to {session_code}"))
                        
                        # Start screen display window
                        self.root.after(0, lambda: self.start_screen_display())
                        
                    else:
                        self.root.after(0, lambda: self.log_activity("Failed to connect as client", "error"))
                        self.root.after(0, lambda: self.reset_client_ui())
                else:
                    self.root.after(0, lambda: self.log_activity("Failed to join session - check session code", "error"))
                    self.root.after(0, lambda: self.reset_client_ui())
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_activity(f"Connection error: {str(e)}", "error"))
                self.root.after(0, lambda: self.reset_client_ui())
        
        threading.Thread(target=client_thread, daemon=True).start()
    
    def disconnect_from_session(self):
        """Disconnect from session"""
        self.log_activity("Disconnected from session", "warning")
        self.client_connect_btn.config(state="normal", bg=self.colors['button_bg'], fg='white')
        self.client_disconnect_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.code_entry.config(state="normal")
        self.code_entry.delete(0, tk.END)
        self.title_status_var.set("●  Ready")
        self.status_var.set("Ready")
        self.client_status_var.set("Not connected")
    
    def reset_client_ui(self):
        """Reset client UI to initial state"""
        self.client_connect_btn.config(state="normal", bg=self.colors['button_bg'], fg='white')
        self.client_disconnect_btn.config(state="disabled", bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.code_entry.config(state="normal")
        self.title_status_var.set("●  Ready")
        self.status_var.set("Ready")
        self.client_status_var.set("Not connected")
        self.relay_connected = False
        self.relay_mode = None
        
    def start_screen_display(self):
        """Start the remote screen display window"""
        try:
            self.log_activity("🖥️ Opening remote desktop window...", "info")
            
            # Create remote viewer - pass self as the app reference
            self.remote_viewer = OptimizedRemoteViewer(self)
            self.remote_viewer.create_viewer_window()
            
            self.log_activity("🎮 Remote desktop window opened - you can now control the remote screen", "success")
            
        except Exception as e:
            self.log_activity(f"❌ Failed to open remote desktop: {str(e)}", "error")
    
    def on_screen_data_received(self, data):
        """Callback when screen data is received from server"""
        try:
            # Forward the screen data to the remote viewer if it exists
            if self.remote_viewer:
                # The data received is base64 encoded, need to create proper format
                import base64
                jpeg_data = base64.b64decode(data)
                screen_data = {'data': jpeg_data}
                self.remote_viewer.update_display(screen_data)
            else:
                # Log that we're receiving data but viewer isn't ready
                print(f"📺 Received screen data: {len(data)} bytes (viewer not ready)")
                
        except Exception as e:
            self.log_activity(f"❌ Error displaying screen data: {str(e)}", "error")
    
    def copy_session_code(self):
        """Copy session code to clipboard"""
        if self.relay_session_id:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.relay_session_id)
            self.log_activity("Session code copied to clipboard", "info")
    
    def log_activity(self, message, level="info"):
        """Add message to activity log with color coding"""
        if not hasattr(self, 'activity_log'):
            # Store logs if log panel hasn't been created yet
            if not hasattr(self, 'pending_logs'):
                self.pending_logs = []
            self.pending_logs.append((message, level))
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.activity_log.config(state="normal")
        
        # Add timestamp
        self.activity_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add message with appropriate color
        if level == "success":
            self.activity_log.insert(tk.END, "✓ ", "success")
        elif level == "error":
            self.activity_log.insert(tk.END, "✗ ", "error")
        elif level == "warning":
            self.activity_log.insert(tk.END, "⚠ ", "warning")
        else:
            self.activity_log.insert(tk.END, "• ", "info")
        
        self.activity_log.insert(tk.END, f"{message}\n", level)
        self.activity_log.see(tk.END)
        self.activity_log.config(state="disabled")
    
    def run(self):
        """Start the application"""
        self.log_activity("IgniteRemote Professional started", "success")
        self.root.mainloop()

if __name__ == "__main__":
    app = IgniteRemotePro()
    app.run()
