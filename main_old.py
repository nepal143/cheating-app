#!/usr/bin/env python3
"""
IgniteRemote - Professional Remote Desktop Solution
Advanced remote desktop application with enterprise-grade security and stealth capabilities.
Version 2.0 - Professional Edition
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
import os
import sys

# Import stealth manager
try:
    from stealth_manager import StealthManager
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("Stealth features not available")
import pystray
from pystray import MenuItem as item
import sys
import os

from optimized_capture import OptimizedScreenCapture, OptimizedRemoteViewer, OptimizedInputHandler
from improved_networking import ImprovedSecureServer, NetworkHelper
from optimized_networking import OptimizedSecureClient
from crypto_utils import CryptoManager
from relay_client import RelayClient

class IgniteRemoteApp:
    def __init__(self):
        # Initialize stealth features first (if available)
        self.stealth_manager = None
        self.stealth_mode_active = False
        if STEALTH_AVAILABLE:
            try:
                self.stealth_manager = StealthManager()
                # Don't enable automatically - wait for user action
            except Exception as e:
                pass  # Silent failure for stealth
        
        self.root = tk.Tk()
        self.root.title("IgniteRemote - Professional Remote Desktop")
        
        # Modern full-screen setup
        self.setup_modern_window()
        
        # Don't hide automatically - let user control stealth mode
        
        # Application state
        self.is_server_running = False
        self.is_client_connected = False
        self.server = None
        self.client = None
        self.connection_key = ""
        
        # Relay server functionality
        self.relay_client = RelayClient("wss://sync-hello.onrender.com")
        self.relay_session_id = None
        self.relay_connected = False
        self.relay_mode = None  # 'host' or 'client'
        
        # System tray
        self.tray_icon = None
        self.is_hidden = False
        
        # Initialize components with optimized versions
        self.screen_capture = OptimizedScreenCapture()
        self.input_handler = OptimizedInputHandler()
        self.crypto_manager = CryptoManager()
        
        self.setup_ui()
        self.setup_tray()
        self.setup_global_hotkeys()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_modern_window(self):
        """Setup modern, professional full-screen window"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set to fullscreen but windowed (90% of screen)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1200, 800)  # Minimum professional size
        
        # Modern window styling
        self.root.configure(bg='#1e1e1e')  # Dark background
        
        # Setup dark theme
        self.setup_dark_theme()
        
        # Make window look professional
        try:
            # Remove window decorations for modern look (optional)
            # self.root.overrideredirect(True)
            pass
        except:
            pass
    
    def setup_dark_theme(self):
        """Setup professional dark theme"""
        # Define color scheme
        self.colors = {
            'bg': '#1e1e1e',           # Dark background
            'surface': '#2d2d2d',      # Surface elements
            'primary': '#0078d4',      # Primary blue
            'accent': '#00bcf2',       # Accent cyan
            'success': '#16c60c',      # Success green
            'warning': '#ff8c00',      # Warning orange
            'error': '#d13438',        # Error red
            'text': '#ffffff',         # Primary text
            'text_secondary': '#b3b3b3', # Secondary text
            'border': '#404040',       # Border color
        }
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Try to use modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure styles for dark theme
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelFrame', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TLabelFrame.Label', background=self.colors['bg'], foreground=self.colors['text'])
        
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TButton', background=self.colors['surface'], foreground=self.colors['text'])
        style.map('TButton', background=[('active', self.colors['primary'])])
        
        # Accent button style for important actions
        style.configure('Accent.TButton', 
                       background=self.colors['primary'], 
                       foreground='white', 
                       font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', 
                 background=[('active', self.colors['accent']),
                           ('pressed', '#005a9e')])
        
        # Success button style
        style.configure('Success.TButton', 
                       background=self.colors['success'], 
                       foreground='white', 
                       font=('Segoe UI', 10))
        
        # Error button style  
        style.configure('Error.TButton', 
                       background=self.colors['error'], 
                       foreground='white', 
                       font=('Segoe UI', 10))
        
        style.configure('TEntry', fieldbackground=self.colors['surface'], foreground=self.colors['text'])
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['surface'], foreground=self.colors['text'])
        style.map('TNotebook.Tab', background=[('selected', self.colors['primary'])])
        
        # Configure text widgets
        self.text_config = {
            'bg': self.colors['surface'],
            'fg': self.colors['text'],
            'insertbackground': self.colors['text'],
            'selectbackground': self.colors['primary'],
            'selectforeground': 'white'
        }
        
    def setup_ui(self):
        """Setup the modern, professional user interface"""
        # Create main container with header
        self.setup_header()
        
        # Main content area
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create professional tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Only include essential professional tabs
        self.setup_cloud_relay_tab()
        self.setup_settings_tab()
        
    def setup_header(self):
        """Setup modern header with branding"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        left_frame.pack(side="left", fill="y", padx=20, pady=10)
        
        # Logo/Icon (create a simple one)
        logo_label = tk.Label(left_frame, text="🚀", font=("Segoe UI", 32), 
                             bg=self.colors['bg'], fg=self.colors['primary'])
        logo_label.pack(side="left")
        
        # Title and subtitle
        title_frame = tk.Frame(left_frame, bg=self.colors['bg'])
        title_frame.pack(side="left", padx=(15, 0), fill="y")
        
        title_label = tk.Label(title_frame, text="IgniteRemote", 
                              font=("Segoe UI", 24, "bold"), 
                              bg=self.colors['bg'], fg=self.colors['text'])
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(title_frame, text="Professional Remote Desktop Solution", 
                                 font=("Segoe UI", 11), 
                                 bg=self.colors['bg'], fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor="w")
        
        # Right side - Status and controls
        right_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        right_frame.pack(side="right", fill="y", padx=20, pady=15)
        
        # Connection status
        self.connection_status_var = tk.StringVar()
        self.connection_status_var.set("🔴 Disconnected")
        
        status_label = tk.Label(right_frame, textvariable=self.connection_status_var,
                               font=("Segoe UI", 12, "bold"),
                               bg=self.colors['bg'], fg=self.colors['text'])
        status_label.pack(anchor="e")
        
        # Quick action buttons
        quick_actions = tk.Frame(right_frame, bg=self.colors['bg'])
        quick_actions.pack(anchor="e", pady=(10, 0))
        
        self.minimize_btn = ttk.Button(quick_actions, text="➖", width=3,
                                      command=self.hide_to_tray)
        self.minimize_btn.pack(side="left", padx=(0, 5))
        
        # Add stealth button if available
        if self.stealth_manager:
            self.header_stealth_btn = ttk.Button(quick_actions, text="🥷", width=3,
                                                command=self.toggle_stealth_mode)
            self.header_stealth_btn.pack(side="left", padx=(0, 5))
        
        # Separator line
        separator = tk.Frame(self.root, height=1, bg=self.colors['border'])
        separator.pack(fill="x")
    
    def setup_cloud_relay_tab(self):
        """Setup the clean, modern cloud relay tab"""
        # Create tab
        relay_frame = ttk.Frame(self.notebook)
        self.notebook.add(relay_frame, text="🌐  Remote Sessions")
        
        # Main content with clean styling
        main_content = tk.Frame(relay_frame, bg=self.colors['bg'])
        main_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title section
        title_section = tk.Frame(main_content, bg=self.colors['bg'])
        title_section.pack(fill="x", pady=(0, 40))
        
        title = tk.Label(title_section, text="IgniteRemote Sessions", 
                        font=("Segoe UI", 32, "bold"), 
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack()
        
        subtitle = tk.Label(title_section, text="Connect instantly from anywhere in the world", 
                           font=("Segoe UI", 16), 
                           bg=self.colors['bg'], fg=self.colors['text_secondary'])
        subtitle.pack(pady=(8, 0))
        
        # Main cards container
        cards_container = tk.Frame(main_content, bg=self.colors['bg'])
        cards_container.pack(fill="both", expand=True)
        
        # Host Card (Left side)
        host_card = tk.Frame(cards_container, bg=self.colors['surface'], 
                            relief="flat", bd=0, padx=40, pady=40)
        host_card.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Host card header
        tk.Label(host_card, text="🖥️", font=("Segoe UI", 48), 
                bg=self.colors['surface'], fg=self.colors['primary']).pack()
        
        tk.Label(host_card, text="Share Your Screen", 
                font=("Segoe UI", 20, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(10, 5))
        
        tk.Label(host_card, text="Let others connect to your desktop", 
                font=("Segoe UI", 12), 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(pady=(0, 30))
        
        # Host controls
        self.relay_host_btn = tk.Button(host_card, text="🚀 Start Sharing", 
                                       font=("Segoe UI", 16, "bold"),
                                       bg=self.colors['success'], fg='white',
                                       relief="raised", bd=3, padx=40, pady=18,
                                       command=self.start_relay_host,
                                       cursor="hand2")
        self.relay_host_btn.pack(pady=(0, 15))
        
        self.relay_stop_host_btn = tk.Button(host_card, text="⏹️ Stop Sharing", 
                                            font=("Segoe UI", 14, "bold"),
                                            bg=self.colors['error'], fg='white',
                                            relief="raised", bd=2, padx=25, pady=12,
                                            command=self.stop_relay_host, state="disabled",
                                            cursor="hand2")
        self.relay_stop_host_btn.pack(pady=(0, 20))
        
        # Session code display
        code_container = tk.Frame(host_card, bg=self.colors['primary'], 
                                 relief="solid", bd=2, padx=25, pady=25)
        code_container.pack(fill="x", pady=(10, 0))
        
        tk.Label(code_container, text="🔑 Session Code", 
                font=("Segoe UI", 12, "bold"), 
                bg=self.colors['primary'], fg='white').pack()
        
        self.relay_code_var = tk.StringVar()
        self.relay_code_var.set("Not Active")
        
        self.code_display = tk.Label(code_container, textvariable=self.relay_code_var, 
                                    font=("JetBrains Mono", 32, "bold"), 
                                    bg='white', fg=self.colors['primary'],
                                    relief="solid", bd=1, padx=15, pady=10)
        self.code_display.pack(pady=(10, 15))
        
        self.copy_relay_btn = tk.Button(code_container, text="📋 Copy Code", 
                                       font=("Segoe UI", 11, "bold"),
                                       bg='white', fg=self.colors['primary'],
                                       relief="flat", bd=0, padx=20, pady=8,
                                       command=self.copy_relay_code, state="disabled",
                                       cursor="hand2")
        self.copy_relay_btn.pack()
        
        # Client Card (Right side)
        client_card = tk.Frame(cards_container, bg=self.colors['surface'], 
                              relief="flat", bd=0, padx=40, pady=40)
        client_card.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        # Client card header
        tk.Label(client_card, text="🔗", font=("Segoe UI", 48), 
                bg=self.colors['surface'], fg=self.colors['accent']).pack()
        
        tk.Label(client_card, text="Connect to Session", 
                font=("Segoe UI", 20, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(10, 5))
        
        tk.Label(client_card, text="Enter a code to control someone's desktop", 
                font=("Segoe UI", 12), 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(pady=(0, 30))
        
        # Client form
        tk.Label(client_card, text="Enter Session Code:", 
                font=("Segoe UI", 12, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(0, 10))
        
        self.relay_code_entry = tk.Entry(client_card, font=("JetBrains Mono", 20, "bold"), 
                                        justify="center", width=10, 
                                        bg='white', fg=self.colors['primary'],
                                        relief="solid", bd=3, insertbackground=self.colors['primary'])
        self.relay_code_entry.pack(pady=(0, 25), ipady=12)
        self.relay_code_entry.bind('<Return>', lambda e: self.connect_relay_client())
        
        # Client controls
        self.relay_connect_btn = tk.Button(client_card, text="🔗 Connect Now", 
                                          font=("Segoe UI", 16, "bold"),
                                          bg=self.colors['accent'], fg='white',
                                          relief="raised", bd=3, padx=40, pady=18,
                                          command=self.connect_relay_client,
                                          cursor="hand2")
        self.relay_connect_btn.pack(pady=(0, 15))
        
        self.relay_disconnect_btn = tk.Button(client_card, text="❌ Disconnect", 
                                             font=("Segoe UI", 14, "bold"),
                                             bg=self.colors['error'], fg='white',
                                             relief="raised", bd=2, padx=25, pady=12,
                                             command=self.disconnect_relay_client, state="disabled",
                                             cursor="hand2")
        self.relay_disconnect_btn.pack()
        
        # Status bar at bottom
        status_bar = tk.Frame(main_content, bg=self.colors['surface'], 
                             relief="flat", bd=0, pady=20)
        status_bar.pack(fill="x", pady=(40, 0))
        
        status_content = tk.Frame(status_bar, bg=self.colors['surface'])
        status_content.pack(fill="x", padx=40)
        
        tk.Label(status_content, text="Status:", font=("Segoe UI", 12, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(side="left")
        
        self.relay_status_var = tk.StringVar()
        self.relay_status_var.set("Ready to connect")
        
        tk.Label(status_content, textvariable=self.relay_status_var, 
                font=("Segoe UI", 12), 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(side="left", padx=(10, 0))
        
        # Activity log (compact)
        log_frame = tk.Frame(main_content, bg=self.colors['bg'])
        log_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(log_frame, text="Activity Log:", font=("Segoe UI", 10, "bold"), 
                bg=self.colors['bg'], fg=self.colors['text']).pack(anchor="w")
        
        self.relay_log = scrolledtext.ScrolledText(log_frame, height=4, 
                                                  bg=self.colors['surface'], 
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['text'],
                                                  font=("Consolas", 9),
                                                  relief="flat", bd=1)
        self.relay_log.pack(fill="x", pady=(5, 0))
        self.relay_log.config(state="disabled")
    
    def setup_settings_tab(self):
        """Setup clean, modern settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️  Settings")
        
        # Main settings content
        main_content = tk.Frame(settings_frame, bg=self.colors['bg'])
        main_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        title = tk.Label(main_content, text="Settings", 
                        font=("Segoe UI", 28, "bold"), 
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack(pady=(0, 30))
        
        # Settings cards container
        cards_container = tk.Frame(main_content, bg=self.colors['bg'])
        cards_container.pack(fill="both", expand=True)
        
        # Performance card
        perf_card = tk.Frame(cards_container, bg=self.colors['surface'], 
                            relief="flat", bd=0, padx=30, pady=30)
        perf_card.pack(fill="x", pady=(0, 20))
        
        tk.Label(perf_card, text="⚡", font=("Segoe UI", 32), 
                bg=self.colors['surface'], fg=self.colors['primary']).pack()
        
        tk.Label(perf_card, text="Performance", 
                font=("Segoe UI", 18, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(10, 20))
        
        # Quality settings
        quality_frame = tk.Frame(perf_card, bg=self.colors['surface'])
        quality_frame.pack()
        
        tk.Label(quality_frame, text="Video Quality:", 
                font=("Segoe UI", 12, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack()
        
        self.quality_var = tk.StringVar(value="High")
        quality_options = tk.Frame(quality_frame, bg=self.colors['surface'])
        quality_options.pack(pady=(10, 0))
        
        for quality in ["Ultra", "High", "Medium"]:
            rb = tk.Radiobutton(quality_options, text=quality, variable=self.quality_var, value=quality,
                               bg=self.colors['surface'], fg=self.colors['text'],
                               selectcolor=self.colors['primary'], font=("Segoe UI", 10))
            rb.pack(side="left", padx=15)
        
        # Security card (if stealth available)
        if self.stealth_manager:
            security_card = tk.Frame(cards_container, bg=self.colors['surface'], 
                                    relief="flat", bd=0, padx=30, pady=30)
            security_card.pack(fill="x", pady=(0, 20))
            
            tk.Label(security_card, text="🥷", font=("Segoe UI", 32), 
                    bg=self.colors['surface'], fg=self.colors['warning']).pack()
            
            tk.Label(security_card, text="Stealth Mode", 
                    font=("Segoe UI", 18, "bold"), 
                    bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(10, 5))
            
            tk.Label(security_card, text="Hide application from system monitoring", 
                    font=("Segoe UI", 11), 
                    bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(pady=(0, 20))
            
            stealth_controls = tk.Frame(security_card, bg=self.colors['surface'])
            stealth_controls.pack()
            
            self.stealth_btn = tk.Button(stealth_controls, text="🥷 Enable Stealth Mode", 
                                        font=("Segoe UI", 12, "bold"),
                                        bg=self.colors['warning'], fg='white',
                                        relief="flat", bd=0, padx=20, pady=10,
                                        command=self.toggle_stealth_mode,
                                        cursor="hand2")
            self.stealth_btn.pack(side="left", padx=(0, 15))
            
            self.stealth_status_var = tk.StringVar()
            self.stealth_status_var.set("Stealth: Disabled")
            tk.Label(stealth_controls, textvariable=self.stealth_status_var, 
                    font=("Segoe UI", 11), 
                    bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(side="left")
        
        # About card
        about_card = tk.Frame(cards_container, bg=self.colors['surface'], 
                             relief="flat", bd=0, padx=30, pady=30)
        about_card.pack(fill="x")
        
        tk.Label(about_card, text="🚀", font=("Segoe UI", 32), 
                bg=self.colors['surface'], fg=self.colors['accent']).pack()
        
        tk.Label(about_card, text="IgniteRemote Professional", 
                font=("Segoe UI", 18, "bold"), 
                bg=self.colors['surface'], fg=self.colors['text']).pack(pady=(10, 5))
        
        tk.Label(about_card, text="Version 2.0 - Enterprise Remote Desktop Solution", 
                font=("Segoe UI", 11), 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(pady=(0, 20))
        
        # Tech specs
        specs_frame = tk.Frame(about_card, bg=self.colors['surface'])
        specs_frame.pack()
        
        specs = [
            ("Encryption", "AES-256"), 
            ("Protocol", "WebSocket"), 
            ("Quality", "1280x800"),
            ("Frame Rate", "25 FPS")
        ]
        
        for i, (label, value) in enumerate(specs):
            spec_frame = tk.Frame(specs_frame, bg=self.colors['bg'], 
                                 relief="flat", bd=0, padx=15, pady=8)
            spec_frame.pack(side="left", padx=5)
            
            tk.Label(spec_frame, text=label, font=("Segoe UI", 9), 
                    bg=self.colors['bg'], fg=self.colors['text_secondary']).pack()
            tk.Label(spec_frame, text=value, font=("Segoe UI", 10, "bold"), 
                    bg=self.colors['bg'], fg=self.colors['primary']).pack()
        
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
        self.stop_server_btn.pack(side="left", padx=(0, 5))
        
        # Network info button
        ttk.Button(controls_frame, text="Show Network Info", command=self.show_network_info).pack(side="left")
        
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
        
        # Reverse connection button for easy access
        self.reverse_btn = ttk.Button(controls_frame, text="🔄 Reverse Connect", command=self.suggest_reverse_connection)
        self.reverse_btn.pack(side="left", padx=(10, 0))
        
        # Connection log
        log_frame = ttk.LabelFrame(parent, text="Connection Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.client_log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.client_log.pack(fill="both", expand=True)
    
    def setup_relay_tab(self, parent):
        """Setup the cloud relay tab (no port forwarding needed)"""
        # Header info
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        title_label = ttk.Label(header_frame, text="🌐 CLOUD RELAY - NO PORT FORWARDING!", 
                               font=("Arial", 12, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Works anywhere in the world • No router setup • Just share codes!", 
                                  font=("Arial", 9), foreground="green")
        subtitle_label.pack(pady=(0, 10))
        
        # Host section
        host_frame = ttk.LabelFrame(parent, text="🖥️ Share Your Screen", padding=10)
        host_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(host_frame, text="Click below to generate a 6-digit session code.").pack(anchor="w")
        ttk.Label(host_frame, text="Share this code with someone to let them view your screen.").pack(anchor="w", pady=(0, 10))
        
        # Host controls
        host_controls = ttk.Frame(host_frame)
        host_controls.pack(fill="x")
        
        self.relay_host_btn = ttk.Button(host_controls, text="🚀 Start Cloud Hosting", 
                                        command=self.start_relay_host, style="Accent.TButton")
        self.relay_host_btn.pack(side="left", padx=(0, 10))
        
        self.relay_stop_host_btn = ttk.Button(host_controls, text="⏹️ Stop Hosting", 
                                             command=self.stop_relay_host, state="disabled")
        self.relay_stop_host_btn.pack(side="left")
        
        # Session code display
        self.relay_code_var = tk.StringVar()
        self.relay_code_var.set("")
        
        code_frame = ttk.Frame(host_frame)
        code_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(code_frame, text="Session Code:").pack(side="left")
        code_display = ttk.Label(code_frame, textvariable=self.relay_code_var, 
                                font=("Courier", 14, "bold"), foreground="blue")
        code_display.pack(side="left", padx=(10, 0))
        
        self.copy_relay_btn = ttk.Button(code_frame, text="📋 Copy Code", 
                                        command=self.copy_relay_code, state="disabled")
        self.copy_relay_btn.pack(side="right")
        
        # Client section
        client_frame = ttk.LabelFrame(parent, text="👀 Connect to Someone", padding=10)
        client_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(client_frame, text="Enter a 6-digit session code to connect:").pack(anchor="w")
        
        # Client controls
        client_controls = ttk.Frame(client_frame)
        client_controls.pack(fill="x", pady=(10, 0))
        
        ttk.Label(client_controls, text="Code:").pack(side="left")
        
        self.relay_code_entry = ttk.Entry(client_controls, font=("Courier", 12, "bold"), 
                                         width=8, justify="center")
        self.relay_code_entry.pack(side="left", padx=(5, 10))
        self.relay_code_entry.bind('<Return>', lambda e: self.connect_relay_client())
        
        self.relay_connect_btn = ttk.Button(client_controls, text="🔗 Connect", 
                                           command=self.connect_relay_client, style="Accent.TButton")
        self.relay_connect_btn.pack(side="left", padx=(0, 10))
        
        self.relay_disconnect_btn = ttk.Button(client_controls, text="❌ Disconnect", 
                                              command=self.disconnect_relay_client, state="disabled")
        self.relay_disconnect_btn.pack(side="left")
        
        # Status and log
        status_frame = ttk.LabelFrame(parent, text="Status & Log", padding=10)
        status_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.relay_status_var = tk.StringVar()
        self.relay_status_var.set("Ready to connect - Choose host or client mode above")
        
        status_label = ttk.Label(status_frame, textvariable=self.relay_status_var, 
                                font=("Arial", 9), foreground="gray")
        status_label.pack(anchor="w", pady=(0, 5))
        
        self.relay_log = scrolledtext.ScrolledText(status_frame, height=6, state="disabled")
        self.relay_log.pack(fill="both", expand=True)
        
        # Stealth Mode section (only show if stealth is available)
        if self.stealth_manager:
            stealth_frame = ttk.LabelFrame(parent, text="🥷 Stealth Mode", padding=10)
            stealth_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(stealth_frame, text="Hide application completely from Task Manager, Process List, and system monitoring.", 
                     font=("Arial", 9)).pack(anchor="w")
            ttk.Label(stealth_frame, text="⚠️ Use responsibly. App will be invisible until you unhide it.", 
                     font=("Arial", 8), foreground="orange").pack(anchor="w", pady=(0, 10))
            
            stealth_controls = ttk.Frame(stealth_frame)
            stealth_controls.pack(fill="x")
            
            self.stealth_btn = ttk.Button(stealth_controls, text="🥷 Enable Stealth Mode", 
                                         command=self.toggle_stealth_mode)
            self.stealth_btn.pack(side="left", padx=(0, 10))
            
            self.stealth_status_var = tk.StringVar()
            self.stealth_status_var.set("Stealth: Disabled")
            stealth_status = ttk.Label(stealth_controls, textvariable=self.stealth_status_var, 
                                      font=("Arial", 9), foreground="gray")
            stealth_status.pack(side="left")
        
    def setup_tray(self):
        """Setup system tray functionality"""
        # Create professional tray icon
        try:
            # Create a more professional icon
            from PIL import Image, ImageDraw
            image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw a modern rocket icon
            draw.ellipse([10, 15, 54, 59], fill='#0078d4')
            draw.polygon([(32, 8), (25, 22), (39, 22)], fill='#00bcf2')
            draw.ellipse([24, 30, 40, 46], fill='white')
            
        except:
            # Fallback to simple icon
            image = Image.new('RGB', (64, 64), color='#0078d4')
        
        # Create professional tray menu
        menu = pystray.Menu(
            item('Show IgniteRemote', self.show_from_tray, default=True),
            item('Hide (Stealth)', self.hide_to_stealth),
            item('Exit Stealth', self.exit_stealth_from_tray, visible=lambda item: self.stealth_mode_active),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("IgniteRemote", image, "IgniteRemote Professional", menu)
        
    def setup_global_hotkeys(self):
        """Setup global hotkeys for stealth mode control"""
        try:
            import keyboard
            # Register global hotkey Ctrl+Alt+Shift+S to toggle stealth
            keyboard.add_hotkey('ctrl+alt+shift+s', self.hotkey_toggle_stealth)
        except ImportError:
            # keyboard module not available
            pass
        except Exception as e:
            # Silent failure for hotkey setup
            pass
    
    def hotkey_toggle_stealth(self):
        """Handle global hotkey for stealth toggle"""
        try:
            if self.stealth_mode_active:
                # Show the application
                self.root.after(0, self.disable_stealth_mode)
            else:
                # Just show the app - don't auto-enable stealth
                self.root.after(0, lambda: (self.root.deiconify(), self.root.lift()))
        except Exception as e:
            pass
        
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
    
    def hide_to_stealth(self, icon=None, item=None):
        """Hide to stealth mode from tray"""
        if self.stealth_manager and not self.stealth_mode_active:
            self.enable_stealth_mode()
    
    def exit_stealth_from_tray(self, icon=None, item=None):
        """Exit stealth mode from tray"""
        if self.stealth_mode_active:
            self.disable_stealth_mode()
            
    def start_server(self):
        """Start the remote desktop server"""
        try:
            # Generate connection key (user selects IP during this step)
            self.connection_key = self.generate_connection_key()
            
            if not self.connection_key:
                return  # User cancelled IP selection
            
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
            self.server = ImprovedSecureServer(self.crypto_manager)
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
            
            self.is_server_running = True
            self.status_var.set("Server running - Waiting for connections")
            
            self.log_to_server(f"✅ Server started successfully!")
            self.log_to_server(f"� Share this key with clients:")
            self.log_to_server(f"� {self.connection_key}")
            self.log_to_server(f"🎯 Key contains server IP - clients connect automatically!")
            self.log_to_server(f"⏳ Waiting for connections...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.log_to_server(f"❌ Error starting server: {str(e)}")
            
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
            
    def show_network_info(self):
        """Show network connection information"""
        try:
            from improved_networking import NetworkHelper
            
            # Show basic info immediately
            network_info = NetworkHelper.get_network_info()
            
            # Detect public IP in background
            def detect_public_ip():
                try:
                    public_ip = NetworkHelper.get_public_ip()
                    network_info['public_ip'] = public_ip
                    network_info['external_connection'] = f"{public_ip}:9999"
                    print(f"Public IP detected: {public_ip}")
                except Exception as e:
                    print(f"Could not detect public IP: {e}")
                    network_info['public_ip'] = "Detection failed"
                    network_info['external_connection'] = "Not available"
            
            # Start detection in background
            threading.Thread(target=detect_public_ip, daemon=True).start()
            
            info_text = f"""🌐 NETWORK CONNECTION INFORMATION

📍 Local IP: {network_info['local_ip']}
🌍 Public IP: {network_info['public_ip']}

📋 CONNECTION INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 SAME NETWORK (WiFi/LAN):
   Use: {network_info['local_connection']}

🌍 DIFFERENT NETWORKS (Internet):
   Use: {network_info['external_connection']}
   
⚠️ For external connections:
• Forward port 9999 in your router
• Allow port 9999 in Windows Firewall
• Some mobile carriers block incoming connections

💡 QUICK TEST:
1. Start the server
2. Test locally first: {network_info['local_connection']}
3. Then test externally: {network_info['external_connection']}

Note: Public IP detection runs in background"""

            messagebox.showinfo("Network Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get network info: {str(e)}")
            
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
                messagebox.showerror("Error", "Invalid connection key format")
                return
            
            self.log_to_client("🔍 Connection key analysis:")
            server_ip = server_info['server_ip']
            
            # Determine connection type based on IP
            if server_ip.startswith('192.168.') or server_ip.startswith('10.') or server_ip.startswith('172.'):
                self.log_to_client("� LOCAL NETWORK connection detected")
                self.log_to_client("💡 If connection fails:")
                self.log_to_client("   • Ensure both devices on same WiFi/network")
                self.log_to_client("   • Check Windows Firewall allows port 9999")
            else:
                self.log_to_client("� INTERNET connection detected")
                self.log_to_client("💡 If connection fails:")
                self.log_to_client("   • Verify server has port forwarding enabled")
                self.log_to_client("   • Check both firewalls allow port 9999")
                self.log_to_client("   • Server might be behind NAT/router")
                
            # Update UI
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            # Start client
            self.client = OptimizedSecureClient(self.crypto_manager)
            client_thread = threading.Thread(target=self.run_client, args=(server_info,), daemon=True)
            client_thread.start()
            
            self.is_client_connected = True
            self.status_var.set("Connecting to server...")
            self.log_to_client(f"🔄 Connecting to: {server_ip}:{server_info['server_port']}...")
            
        except Exception as e:
            error_msg = str(e)
            self.log_to_client(f"❌ Connection setup error: {error_msg}")
            
            # Show reverse connection suggestion for timeouts and connection refused
            if any(code in error_msg for code in ["10060", "10061", "timeout", "Failed to connect", "refused"]):
                self.log_to_client("🔧 Connection Failed - Port Forwarding Issue:")
                self.log_to_client("   • Server's router isn't forwarding port 9999")
                self.log_to_client("   • Firewall blocking the connection")
                self.log_to_client("   • Server not accessible from internet")
                self.log_to_client("")
                self.log_to_client("💡 INSTANT FIX - Try Reverse Connection:")
                self.log_to_client("   1. Person sharing screen: Use CLIENT mode")
                self.log_to_client("   2. Person viewing: Use SERVER mode")
                self.log_to_client("   3. Viewer shares connection key to screen sharer")
                self.log_to_client("   4. No port forwarding needed!")
                
                # Offer to switch to reverse connection mode
                reverse_choice = messagebox.askyesno(
                    "Connection Failed - Try Reverse Connection?",
                    "Connection failed due to port forwarding issues.\n\n" +
                    "SOLUTION: Use Reverse Connection Method\n\n" +
                    "Would you like to switch to reverse connection?\n" +
                    "• You become the SERVER (no port forwarding needed)\n" +
                    "• Other person connects to you as CLIENT\n" +
                    "• Works behind any firewall/router"
                )
                
                if reverse_choice:
                    self.log_to_client("🔄 Switching to Reverse Connection Mode...")
                    self.log_to_client("📋 Instructions:")
                    self.log_to_client("1. Click 'Server' tab")
                    self.log_to_client("2. Start server and share connection key")
                    self.log_to_client("3. Ask other person to connect as client")
                    
                    # Switch to server tab
                    self.notebook.select(0)  # Switch to server tab
                    messagebox.showinfo("Reverse Connection", 
                        "Switched to Server mode.\n\n" +
                        "Now:\n" +
                        "1. Start the server\n" +
                        "2. Share your connection key\n" +
                        "3. Wait for other person to connect")
            
            # Provide specific help for common errors
            elif "getaddrinfo failed" in error_msg:
                self.log_to_client("🔧 DNS/Network Resolution Error:")
                self.log_to_client("   • Check internet connection")
                self.log_to_client("   • Verify IP address is correct")
                self.log_to_client("   • Connection key might have invalid IP")
                self.log_to_client("   • Try restarting network adapter")
                messagebox.showerror("Network Error", 
                    "Cannot resolve server address.\n\n" +
                    "Possible causes:\n" +
                    "• Internet connection down\n" +
                    "• Invalid IP in connection key\n" +
                    "• Network/DNS configuration issue\n" +
                    "• Firewall blocking connection")
            elif "10061" in error_msg:
                self.log_to_client("🔧 Connection Refused Error:")
                self.log_to_client("   • Server is reachable but port 9999 is closed")
                self.log_to_client("   • Router/firewall blocking port 9999")
                self.log_to_client("   • Server not listening on port 9999")
                self.log_to_client("   • Need port forwarding for internet connections")
                messagebox.showerror("Connection Refused", 
                    "Server refused the connection.\n\n" +
                    "SOLUTION NEEDED:\n" +
                    "• Server must forward port 9999 in router\n" +
                    "• Allow port 9999 in Windows Firewall\n" +
                    "• Verify server is actually running\n\n" +
                    "This is typically a port forwarding issue!")
            elif "11001" in error_msg:
                self.log_to_client("🔧 DNS Resolution Error:")
                self.log_to_client("   • Cannot resolve server IP address")
                self.log_to_client("   • Check internet connection")
                self.log_to_client("   • Invalid IP in connection key")
                messagebox.showerror("DNS Error", 
                    "Cannot resolve server address.\n\n" +
                    "Please check:\n" +
                    "• Internet connection\n" +
                    "• Connection key has valid IP\n" +
                    "• DNS server is working")
            else:
                messagebox.showerror("Error", f"Failed to connect: {error_msg}")
                
            # Reset UI state
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            
    def suggest_reverse_connection(self):
        """Suggest using reverse connection method"""
        result = messagebox.askyesno(
            "Reverse Connection Method",
            "🔄 REVERSE CONNECTION SOLUTION\n\n" +
            "Instead of connecting TO a server, YOU become the server!\n\n" +
            "HOW IT WORKS:\n" +
            "• You: Switch to SERVER mode (no port forwarding needed)\n" +
            "• Other person: Uses CLIENT mode to connect to you\n" +
            "• Perfect for bypassing firewalls and NAT routers\n\n" +
            "Would you like to switch to Server mode now?"
        )
        
        if result:
            # Switch to server tab
            self.notebook.select(0)  # Switch to server tab
            self.log_to_server("🔄 Switched to Reverse Connection Mode")
            self.log_to_server("📋 Instructions:")
            self.log_to_server("1. Click 'Start Server'")
            self.log_to_server("2. Share your connection key with the other person")
            self.log_to_server("3. Wait for them to connect as client")
            self.log_to_server("4. No port forwarding required!")
            
            messagebox.showinfo("Reverse Connection", 
                "Switched to Server mode!\n\n" +
                "Next steps:\n" +
                "1. Start the server\n" +
                "2. Share connection key with other person\n" +
                "3. They connect to you as client\n\n" +
                "This bypasses all port forwarding issues!")

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
        """Generate a secure connection key with user-selected IP"""
        from improved_networking import NetworkHelper
        
        # Get network info first
        self.log_to_server("🔍 Getting network information...")
        network_info = NetworkHelper.get_network_info()
        
        # Show current IPs to user
        self.log_to_server(f"📍 Local IP: {network_info['local_ip']}")
        self.log_to_server(f"🌍 Public IP: {network_info['public_ip']}")
        
        # Ask user which IP to include in the connection key
        if network_info['public_ip'] in ["Unable to detect", "Detection failed"]:
            # If public IP detection failed, offer manual entry
            ip_choice = messagebox.askyesnocancel(
                "Connection Key IP",
                f"Local IP: {network_info['local_ip']}\n" +
                f"Public IP: {network_info['public_ip']}\n\n" +
                "Which IP should be included in the connection key?\n\n" +
                "YES = Local IP (same network only)\n" +
                "NO = Manual IP entry (type your own)\n" +
                "CANCEL = Cancel key generation"
            )
        else:
            # Both IPs available
            ip_choice = messagebox.askyesnocancel(
                "Connection Key IP",
                f"Local IP: {network_info['local_ip']}\n" +
                f"Public IP: {network_info['public_ip']}\n\n" +
                "Which IP should be included in the connection key?\n\n" +
                f"YES = Public IP ({network_info['public_ip']}) - For Internet\n" +
                f"NO = Local IP ({network_info['local_ip']}) - For same network\n" +
                "CANCEL = Manual IP entry"
            )
        
        if ip_choice is True:  # Public IP or Local IP (depending on availability)
            if network_info['public_ip'] not in ["Unable to detect", "Detection failed"]:
                server_ip = network_info['public_ip']
                self.log_to_server(f"✅ Using public IP: {server_ip}")
            else:
                server_ip = network_info['local_ip']
                self.log_to_server(f"✅ Using local IP (public detection failed): {server_ip}")
        elif ip_choice is False:  # Local IP or Manual entry
            if network_info['public_ip'] not in ["Unable to detect", "Detection failed"]:
                server_ip = network_info['local_ip']
                self.log_to_server(f"✅ Using local IP: {server_ip}")
            else:
                server_ip = self.manual_ip_entry("Enter the server IP address:")
        else:  # Manual entry or Cancel
            if network_info['public_ip'] not in ["Unable to detect", "Detection failed"]:
                server_ip = self.manual_ip_entry("Enter the server IP address:")
            else:
                return None  # User cancelled
        
        if not server_ip or not self.validate_ip(server_ip):
            self.log_to_server(f"❌ Invalid IP address: {server_ip}")
            messagebox.showerror("Invalid IP", f"Invalid IP address: {server_ip}\nPlease try again.")
            return None
        
        # Generate random key components
        session_id = secrets.token_hex(16)
        server_port = 9999  # Default port
        timestamp = int(time.time())
        
        # Create key data with selected IP
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
        
        self.log_to_server(f"✅ Connection key generated with IP: {server_ip}")
        self.log_to_server(f"📋 Clients should connect to: {server_ip}:9999")
        
        return key_b64
    
    def manual_ip_entry(self, prompt):
        """Get IP address from user input"""
        from tkinter import simpledialog
        
        ip = simpledialog.askstring("IP Address", prompt + "\n\nExample: 192.168.1.100 or 103.83.212.76")
        if ip:
            ip = ip.strip()
            # Basic validation
            if self.validate_ip(ip):
                return ip
            else:
                messagebox.showerror("Invalid IP", "Please enter a valid IP address")
                return self.manual_ip_entry(prompt)
        return None
    
    def validate_ip(self, ip):
        """Enhanced IP address validation"""
        if not ip or not isinstance(ip, str):
            return False
            
        ip = ip.strip()
        
        # Check for empty or invalid characters
        if not ip or any(c not in '0123456789.' for c in ip):
            return False
            
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part or int(part) < 0 or int(part) > 255:
                    return False
            return True
        except (ValueError, AttributeError):
            return False
    
    def test_ip_connectivity(self, ip):
        """Test if an IP address is reachable"""
        try:
            import socket
            # Try to resolve the IP
            socket.gethostbyaddr(ip)
            return True
        except:
            try:
                # Try basic socket connection test
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)  # 2 second timeout
                    result = s.connect_ex((ip, 9999))
                    return result == 0  # 0 means success
            except:
                return False
        
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
                self.log_to_client("⚠️ Warning: Connection key is more than 24 hours old")
            
            # Log extracted server info
            self.log_to_client(f"📋 Connection key decoded successfully!")
            self.log_to_client(f"🎯 Server IP from key: {key_data['server_ip']}")
            self.log_to_client(f"🚪 Server Port: {key_data['server_port']}")
            
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
            success, network_info = self.server.start(port=9999)
            
            if success and network_info:
                self.log_to_server("Server started successfully!")
                self.log_to_server(f"Local connection: {network_info['local_connection']}")
                self.log_to_server("Public IP detection in progress...")
                self.log_to_server("Share the connection info with remote users")
                self.log_to_server("Note: For external networks, port 9999 must be forwarded in your router")
                self.log_to_server("Waiting for client connections...")
                
                # Keep server alive while running
                while self.is_server_running:
                    time.sleep(1)
                    
            else:
                self.log_to_server("Failed to start server. Check if port 9999 is available.")
                
        except Exception as e:
            self.log_to_server(f"Server error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Server Error", str(e)))
        finally:
            if hasattr(self, 'server') and self.server:
                self.server.stop()
            
    def run_client(self, server_info):
        """Run the client in a separate thread"""
        try:
            # Set up the callback for receiving screen data
            self.client.set_receive_callback(self.update_remote_viewer)
            
            success = self.client.connect(server_info['server_ip'], server_info['server_port'])
            
            if success:
                self.log_to_client("Connected successfully to remote desktop")
                self.status_var.set("Connected - Receiving remote desktop")
                
                # Open remote desktop viewer window
                self.open_remote_viewer()
                
                self.log_to_client("Screen data reception started automatically")
                
                # Keep connection alive while connected
                while self.is_client_connected and self.client.is_connected:
                    time.sleep(1)  # Just keep alive, data comes through callback
                        
            else:
                self.log_to_client("Failed to connect to server")
                self.log_to_client("💡 TRY REVERSE CONNECTION - Click '🔄 Reverse Connect' button!")
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
        
        def create_viewer():
            self.remote_viewer = OptimizedRemoteViewer(self)
            self.remote_viewer.create_viewer_window()
            
        # Create viewer in main thread
        self.root.after(0, create_viewer)
        self.log_to_client("Remote desktop viewer opened")
        
    def update_remote_viewer(self, screen_data):
        """Update the remote desktop viewer with new screen data"""
        if hasattr(self, 'remote_viewer') and self.remote_viewer and self.remote_viewer.viewer_window:
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
    
    # ===============================
    # RELAY SERVER METHODS (CLOUD)
    # ===============================
    
    def setup_relay_callbacks(self):
        """Setup relay client callbacks"""
        self.relay_client.on_screen_data = self.handle_relay_screen_data
        self.relay_client.on_input_data = self.handle_relay_input_data  
        self.relay_client.on_connection_change = self.handle_relay_connection_change
    
    def start_relay_host(self):
        """Start hosting via relay server"""
        self.log_to_relay("🔄 Creating cloud session...")
        self.relay_status_var.set("Creating session...")
        self.relay_host_btn.config(state="disabled")
        
        def host_thread():
            try:
                self.setup_relay_callbacks()
                
                # Create session
                session_id = self.relay_client.create_session()
                if not session_id:
                    self.log_to_relay("❌ Failed to create session")
                    self.relay_status_var.set("Failed to create session")
                    self.root.after(0, lambda: self.relay_host_btn.config(state="normal"))
                    return
                
                self.relay_session_id = session_id
                
                # Update UI on main thread
                self.root.after(0, lambda: self.relay_code_var.set(session_id))
                self.root.after(0, lambda: self.code_display.config(fg='#27ae60'))
                self.root.after(0, lambda: self.copy_relay_btn.config(state="normal"))
                
                # Connect as host
                if self.relay_client.connect_as_host():
                    self.relay_connected = True
                    self.relay_mode = 'host'
                    self.root.after(0, lambda: self.log_to_relay(f"✅ Hosting session: {session_id}"))
                    self.root.after(0, lambda: self.relay_status_var.set(f"🟢 Active - Session: {session_id}"))
                    
                    self.root.after(0, lambda: self.update_relay_host_ui(True))
                    
                    # Start screen sharing
                    self.start_relay_screen_sharing()
                else:
                    self.root.after(0, lambda: self.log_to_relay("❌ Failed to connect as host"))
                    self.root.after(0, lambda: self.relay_status_var.set("Failed to connect as host"))
                    self.root.after(0, lambda: self.relay_host_btn.config(state="normal"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_to_relay(f"❌ Host error: {e}"))
                self.root.after(0, lambda: self.relay_status_var.set(f"Error: {e}"))
                self.root.after(0, lambda: self.relay_host_btn.config(state="normal"))
                
        threading.Thread(target=host_thread, daemon=True).start()
    
    def stop_relay_host(self):
        """Stop relay hosting"""
        self.relay_connected = False
        self.relay_mode = None
        
        if self.relay_client:
            self.relay_client.disconnect()
            
        self.log_to_relay("🛑 Stopped hosting")
        self.relay_status_var.set("Stopped hosting")
        self.update_relay_host_ui(False)
    
    def connect_relay_client(self):
        """Connect as relay client"""
        session_code = self.relay_code_entry.get().strip().upper()
        if not session_code:
            messagebox.showerror("Error", "Please enter session code")
            return
            
        if len(session_code) != 6:
            messagebox.showerror("Error", "Session code must be 6 characters")
            return
        
        self.log_to_relay(f"🔄 Connecting to session: {session_code}")
        self.relay_status_var.set(f"Connecting to {session_code}...")
        self.relay_connect_btn.config(state="disabled")
        
        def connect_thread():
            try:
                self.setup_relay_callbacks()
                
                if self.relay_client.connect_as_client(session_code):
                    self.relay_connected = True
                    self.relay_mode = 'client'
                    self.relay_session_id = session_code
                    
                    self.log_to_relay(f"✅ Connected to session: {session_code}")
                    self.relay_status_var.set(f"Connected to {session_code} - Receiving screen...")
                    
                    self.root.after(0, lambda: self.update_relay_client_ui(True))
                    
                    # Open remote viewer for relay connection
                    self.root.after(0, self.open_remote_viewer)
                else:
                    self.log_to_relay(f"❌ Failed to connect to {session_code}")
                    self.relay_status_var.set("Connection failed")
                    self.relay_connect_btn.config(state="normal")
                    
            except Exception as e:
                self.log_to_relay(f"❌ Connection error: {e}")
                self.relay_status_var.set(f"Error: {e}")
                self.relay_connect_btn.config(state="normal")
                
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_relay_client(self):
        """Disconnect relay client"""
        self.relay_connected = False
        self.relay_mode = None
        
        if self.relay_client:
            self.relay_client.disconnect()
            
        self.log_to_relay("📴 Disconnected from session")
        self.relay_status_var.set("Disconnected")
        self.update_relay_client_ui(False)
    
    def start_relay_screen_sharing(self):
        """Start sharing screen via relay"""
        def share_loop():
            frame_time = 1/25  # 25 FPS for better performance and smoothness
            last_capture_time = 0
            
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
                                self.log_to_relay("❌ Failed to send screen data")
                                # Don't break immediately, try again
                        
                        # Reduced sleep to prevent CPU overload but maintain speed
                        time.sleep(0.005)  # 5ms
                    else:
                        # Much smaller sleep for better responsiveness
                        time.sleep(0.001)  # 1ms
                    
                except Exception as e:
                    self.log_to_relay(f"❌ Screen sharing error: {e}")
                    time.sleep(0.05)  # Shorter pause on error
                    continue  # Don't break, try to recover
                    
        threading.Thread(target=share_loop, daemon=True).start()
    
    def handle_relay_screen_data(self, data):
        """Handle received screen data from relay"""
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
            self.log_to_relay(f"❌ Error handling screen data: {e}")
    
    def handle_relay_input_data(self, data):
        """Handle received input data from relay"""
        try:
            if self.relay_mode == 'host':
                # Process input on host side using the correct method
                self.input_handler.handle_remote_input(data)
        except Exception as e:
            self.log_to_relay(f"❌ Error handling input: {e}")
    
    def handle_relay_connection_change(self, status):
        """Handle relay connection status changes"""
        self.log_to_relay(f"🔄 Connection status: {status}")
        
        if status == 'client_connected':
            self.root.after(0, lambda: self.relay_status_var.set("🎉 Client connected! Screen sharing active."))
            self.root.after(0, lambda: self.connection_status_var.set("🟢 Connected - Sharing"))
        elif status == 'host_available':
            self.root.after(0, lambda: self.relay_status_var.set("🎉 Host available! Receiving screen data..."))
            self.root.after(0, lambda: self.connection_status_var.set("🟢 Connected - Viewing"))
        elif status in ['host_disconnected', 'client_disconnected']:
            self.root.after(0, lambda: self.relay_status_var.set("📴 Other party disconnected"))
            self.root.after(0, lambda: self.connection_status_var.set("🔴 Disconnected"))
    
    def update_relay_host_ui(self, is_hosting):
        """Update relay host UI state"""
        if is_hosting:
            self.relay_host_btn.config(state="disabled", text="🟢 SESSION ACTIVE")
            self.relay_stop_host_btn.config(state="normal")
            # Ensure session code is visible and properly colored
            if hasattr(self, 'code_display'):
                self.code_display.config(fg='#27ae60')  # Green for active
            if hasattr(self, 'relay_code_var') and hasattr(self, 'relay_session_id'):
                if self.relay_session_id:
                    self.relay_code_var.set(self.relay_session_id)
        else:
            self.relay_host_btn.config(state="normal", text="🚀 Start Sharing")
            self.relay_stop_host_btn.config(state="disabled")
            self.copy_relay_btn.config(state="disabled")
            self.relay_code_var.set("Not Active")
            if hasattr(self, 'code_display'):
                self.code_display.config(fg='#e74c3c')  # Red for inactive
    
    def update_relay_client_ui(self, is_connected):
        """Update relay client UI state"""
        if is_connected:
            self.relay_connect_btn.config(state="disabled")
            self.relay_disconnect_btn.config(state="normal")
            self.relay_code_entry.config(state="disabled")
        else:
            self.relay_connect_btn.config(state="normal")
            self.relay_disconnect_btn.config(state="disabled") 
            self.relay_code_entry.config(state="normal")
    
    def copy_relay_code(self):
        """Copy relay session code to clipboard"""
        if self.relay_session_id:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.relay_session_id)
            self.log_to_relay("📋 Session code copied to clipboard")
        else:
            self.log_to_relay("❌ No session code to copy")
    
    def log_to_relay(self, message):
        """Add message to relay log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.relay_log.config(state="normal")
        self.relay_log.insert(tk.END, log_message)
        self.relay_log.see(tk.END)
        self.relay_log.config(state="disabled")
        
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
            
        # Disconnect relay if connected
        if self.relay_connected:
            self.relay_client.disconnect()
            
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
            
        # Close application
        self.root.quit()
        sys.exit(0)
    
    def toggle_stealth_mode(self):
        """Toggle stealth mode on/off"""
        if not self.stealth_manager:
            messagebox.showerror("Error", "Stealth features not available")
            return
        
        if not self.stealth_mode_active:
            # Enable stealth mode
            result = messagebox.askyesno(
                "Enable Stealth Mode",
                "This will hide the application completely from:\n"
                "• Task Manager\n"
                "• Process lists\n"
                "• System monitoring tools\n\n"
                "You can unhide by:\n"
                "• Right-clicking the system tray icon\n"
                "• Using the keyboard shortcut Ctrl+Alt+Shift+S\n\n"
                "Continue?"
            )
            
            if result:
                self.enable_stealth_mode()
        else:
            # Disable stealth mode
            self.disable_stealth_mode()
    
    def enable_stealth_mode(self):
        """Enable stealth features"""
        try:
            self.log_to_relay("🥷 Enabling stealth mode...")
            
            # Enable stealth in background thread
            def enable_stealth():
                success = self.stealth_manager.enable_full_stealth()
                if success:
                    self.stealth_mode_active = True
                    self.root.after(0, self._update_stealth_ui)
                    self.stealth_manager.monitor_detection()
                    
                    # Hide main window after 3 seconds
                    time.sleep(3)
                    self.root.after(0, self.root.withdraw)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to enable stealth mode"))
            
            threading.Thread(target=enable_stealth, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable stealth mode: {e}")
    
    def disable_stealth_mode(self):
        """Disable stealth features"""
        try:
            self.stealth_mode_active = False
            self._update_stealth_ui()
            self.log_to_relay("👁️ Stealth mode disabled")
            
            # Show window if hidden
            self.root.deiconify()
            self.root.lift()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable stealth mode: {e}")
    
    def _update_stealth_ui(self):
        """Update stealth mode UI"""
        try:
            # Update header stealth button if it exists
            if hasattr(self, 'header_stealth_btn'):
                if self.stealth_mode_active:
                    self.header_stealth_btn.config(text="👁️")
                else:
                    self.header_stealth_btn.config(text="🥷")
            
            # Update settings stealth button if it exists  
            if hasattr(self, 'stealth_btn'):
                if self.stealth_mode_active:
                    self.stealth_btn.config(text="👁️ Disable Stealth Mode")
                else:
                    self.stealth_btn.config(text="🥷 Enable Stealth Mode")
            
            # Update stealth status if it exists
            if hasattr(self, 'stealth_status_var'):
                if self.stealth_mode_active:
                    self.stealth_status_var.set("Stealth: ACTIVE - App will hide soon")
                else:
                    self.stealth_status_var.set("Stealth: Disabled")
                    
            # Update connection status in header
            if hasattr(self, 'connection_status_var'):
                if self.stealth_mode_active:
                    self.connection_status_var.set("🥷 Stealth Mode Active")
                elif hasattr(self, 'relay_connected') and self.relay_connected:
                    self.connection_status_var.set("🟢 Connected")
                else:
                    self.connection_status_var.set("🔴 Disconnected")
                    
        except Exception as e:
            # Silent failure for UI updates
            pass
    
    def _enable_stealth(self):
        """Enable stealth features in background thread (deprecated - now manual)"""
        # This method is now deprecated since we made stealth manual
        pass
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = IgniteRemoteApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")
