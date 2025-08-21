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
            # Ask user about connection type
            connection_choice = messagebox.askyesnocancel(
                "Connection Type",
                "What type of connections do you expect?\n\n" +
                "YES = Internet connections (different networks)\n" +
                "NO = Same network only (WiFi/LAN)\n" +
                "CANCEL = Show both connection options"
            )
            
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
            self.server = ImprovedSecureServer(self.crypto_manager)
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
            
            self.is_server_running = True
            
            # Show appropriate connection info based on user choice
            if connection_choice is True:  # Internet connections
                self.status_var.set("Server running - Internet mode (port forwarding required)")
                self.log_to_server(f"🌍 INTERNET MODE ACTIVATED")
                self.log_to_server(f"📋 Connection key: {self.connection_key}")
                self.log_to_server(f"⚠️ IMPORTANT: Forward port 9999 in your router!")
                self.log_to_server(f"📱 Tell clients to use: YOUR_PUBLIC_IP:9999")
                self.log_to_server(f"💡 Get your public IP from: whatismyipaddress.com")
            elif connection_choice is False:  # LAN only
                self.status_var.set("Server running - Local network mode")
                self.log_to_server(f"🏠 LOCAL NETWORK MODE")
                self.log_to_server(f"📋 Connection key: {self.connection_key}")
                self.log_to_server(f"📍 Tell clients to use your local IP + :9999")
                self.log_to_server(f"💡 Find local IP in Network Info button")
            else:  # Show both
                self.status_var.set("Server running - Both local and internet")
                self.log_to_server(f"🌐 UNIVERSAL MODE")
                self.log_to_server(f"📋 Connection key: {self.connection_key}")
                self.log_to_server(f"🏠 Local: Use local IP + :9999")
                self.log_to_server(f"🌍 Internet: Use public IP + :9999 (needs port forwarding)")
            
            self.log_to_server(f"✅ Server started successfully - Waiting for connections...")
            
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
            
            # Ask about connection type
            is_internet = messagebox.askyesno(
                "Connection Type",
                "Are you connecting over the Internet?\n\n" +
                "YES = Internet connection (different networks)\n" +
                "NO = Same network (WiFi/LAN)\n\n" +
                "This helps with connection troubleshooting."
            )
            
            # Parse connection key to get server info
            server_info = self.parse_connection_key(key)
            if not server_info:
                messagebox.showerror("Error", "Invalid connection key")
                return
            
            # Show different guidance based on connection type
            if is_internet:
                self.log_to_client("🌍 INTERNET CONNECTION MODE")
                self.log_to_client("💡 If connection fails:")
                self.log_to_client("   • Check server's public IP is correct")
                self.log_to_client("   • Verify port 9999 is forwarded on server's router")
                self.log_to_client("   • Check both firewalls allow port 9999")
            else:
                self.log_to_client("🏠 LOCAL NETWORK MODE")
                self.log_to_client("💡 If connection fails:")
                self.log_to_client("   • Ensure both devices on same WiFi/network")
                self.log_to_client("   • Check server's local IP is correct")
                self.log_to_client("   • Try disabling Windows Firewall temporarily")
                
            # Update UI
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            # Start client
            self.client = OptimizedSecureClient(self.crypto_manager)
            client_thread = threading.Thread(target=self.run_client, args=(server_info,), daemon=True)
            client_thread.start()
            
            self.is_client_connected = True
            self.status_var.set("Connecting to server...")
            self.log_to_client(f"🔄 Attempting connection to: {server_info['server_ip']}:{server_info['server_port']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            self.log_to_client(f"❌ Connection error: {str(e)}")
            
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
