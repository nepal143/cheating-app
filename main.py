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

from optimized_capture import OptimizedScreenCapture, OptimizedRemoteViewer, OptimizedInputHandler
from improved_networking import ImprovedSecureServer, NetworkHelper
from optimized_networking import OptimizedSecureClient
from crypto_utils import CryptoManager
from relay_client import RelayClient

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
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Relay Server tab (NEW - No Port Forwarding!)
        relay_frame = ttk.Frame(self.notebook)
        self.notebook.add(relay_frame, text="🌐 Cloud Relay (Easy)")
        self.setup_relay_tab(relay_frame)
        
        # Server tab
        server_frame = ttk.Frame(self.notebook)
        self.notebook.add(server_frame, text="🖥️ Direct Host")
        self.setup_server_tab(server_frame)
        
        # Client tab
        client_frame = ttk.Frame(self.notebook)
        self.notebook.add(client_frame, text="👀 Direct Connect")
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
                    self.relay_host_btn.config(state="normal")
                    return
                
                self.relay_session_id = session_id
                self.relay_code_var.set(session_id)
                self.copy_relay_btn.config(state="normal")
                
                # Connect as host
                if self.relay_client.connect_as_host():
                    self.relay_connected = True
                    self.relay_mode = 'host'
                    self.log_to_relay(f"✅ Hosting session: {session_id}")
                    self.relay_status_var.set(f"Hosting session {session_id} - Share the code!")
                    
                    self.root.after(0, lambda: self.update_relay_host_ui(True))
                    
                    # Start screen sharing
                    self.start_relay_screen_sharing()
                else:
                    self.log_to_relay("❌ Failed to connect as host")
                    self.relay_status_var.set("Failed to connect as host")
                    self.relay_host_btn.config(state="normal")
                    
            except Exception as e:
                self.log_to_relay(f"❌ Host error: {e}")
                self.relay_status_var.set(f"Error: {e}")
                self.relay_host_btn.config(state="normal")
                
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
            frame_time = 1/15  # 15 FPS for better performance (was 30 FPS)
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
                        
                        # Small sleep to prevent CPU overload
                        time.sleep(0.01)  # 10ms
                    else:
                        # Sleep until next frame is due
                        time.sleep(0.005)  # 5ms
                    
                except Exception as e:
                    self.log_to_relay(f"❌ Screen sharing error: {e}")
                    time.sleep(0.1)  # Brief pause on error
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
                # Log input for debugging
                self.log_to_relay(f"🎮 Received input: {data.get('type', 'unknown')} - {data}")
                # Process input on host side using the correct method
                self.input_handler.handle_remote_input(data)
        except Exception as e:
            self.log_to_relay(f"❌ Error handling input: {e}")
    
    def handle_relay_connection_change(self, status):
        """Handle relay connection status changes"""
        self.log_to_relay(f"🔄 Connection status: {status}")
        
        if status == 'client_connected':
            self.root.after(0, lambda: self.relay_status_var.set("🎉 Client connected! Screen sharing active."))
        elif status == 'host_available':
            self.root.after(0, lambda: self.relay_status_var.set("🎉 Host available! Receiving screen data..."))
        elif status in ['host_disconnected', 'client_disconnected']:
            self.root.after(0, lambda: self.relay_status_var.set("📴 Other party disconnected"))
    
    def update_relay_host_ui(self, is_hosting):
        """Update relay host UI state"""
        if is_hosting:
            self.relay_host_btn.config(state="disabled")
            self.relay_stop_host_btn.config(state="normal")
        else:
            self.relay_host_btn.config(state="normal") 
            self.relay_stop_host_btn.config(state="disabled")
            self.copy_relay_btn.config(state="disabled")
            self.relay_code_var.set("")
    
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
