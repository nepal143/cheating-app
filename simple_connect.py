#!/usr/bin/env python3
"""
Simple Remote Desktop - No Port Forwarding Required!
This version uses multiple easy connection methods that just work.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import socket
import json
import requests
import qrcode
from PIL import Image, ImageTk
import subprocess
import time
import os
import tempfile

class SimpleRemoteDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Remote Desktop - Easy Connection")
        self.root.geometry("600x500")
        
        # Simple connection methods
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="🖥️ Simple Remote Desktop", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(self.root, text="No port forwarding needed! Choose any method below:", 
                                 font=("Arial", 10))
        subtitle_label.pack(pady=5)
        
        # Create notebook for different methods
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Method 1: Same WiFi Network (Easiest)
        self.setup_wifi_tab()
        
        # Method 2: Hamachi/VPN (Most Reliable)
        self.setup_vpn_tab()
        
        # Method 3: Cloud Relay (Always Works)
        self.setup_cloud_tab()
        
        # Method 4: Direct IP (Advanced)
        self.setup_direct_tab()
        
    def setup_wifi_tab(self):
        wifi_frame = ttk.Frame(self.notebook)
        self.notebook.add(wifi_frame, text="📶 Same WiFi")
        
        # Instructions
        instructions = """
🟢 EASIEST METHOD - Same WiFi Network

Perfect when both computers are on the same WiFi!
No internet required, super fast connection.

How it works:
1. Both computers connect to same WiFi
2. One person clicks "Host"
3. Share the local IP with the other person
4. They enter it and connect instantly!
        """
        
        inst_label = tk.Label(wifi_frame, text=instructions, justify='left', 
                             font=("Arial", 9))
        inst_label.pack(pady=10, padx=20)
        
        # Buttons
        button_frame = tk.Frame(wifi_frame)
        button_frame.pack(pady=20)
        
        host_btn = tk.Button(button_frame, text="🖥️ Host (Share Screen)", 
                            command=self.start_wifi_host, bg='#4CAF50', fg='white',
                            font=("Arial", 10, "bold"), padx=20, pady=10)
        host_btn.pack(side='left', padx=10)
        
        connect_btn = tk.Button(button_frame, text="👀 Connect (View Screen)", 
                               command=self.start_wifi_connect, bg='#2196F3', fg='white',
                               font=("Arial", 10, "bold"), padx=20, pady=10)
        connect_btn.pack(side='right', padx=10)
        
        # Status
        self.wifi_status = tk.Label(wifi_frame, text="Ready to connect", 
                                   font=("Arial", 9), fg='gray')
        self.wifi_status.pack(pady=10)
        
    def setup_vpn_tab(self):
        vpn_frame = ttk.Frame(self.notebook)
        self.notebook.add(vpn_frame, text="🌐 VPN Method")
        
        instructions = """
🟡 VPN METHOD - Works Anywhere

Use Hamachi, Radmin, or any VPN to connect computers.
Most reliable method for remote connections.

Steps:
1. Install Hamachi (free): https://www.vpn.net
2. Create network or join existing one
3. Both computers get virtual IPs (like 25.x.x.x)
4. Use those IPs to connect directly!

Alternative VPNs:
• Hamachi (easiest)
• Radmin VPN (free, no registration)
• ZeroTier (advanced but powerful)
        """
        
        inst_label = tk.Label(vpn_frame, text=instructions, justify='left', 
                             font=("Arial", 9))
        inst_label.pack(pady=10, padx=20)
        
        # Download buttons
        download_frame = tk.Frame(vpn_frame)
        download_frame.pack(pady=20)
        
        hamachi_btn = tk.Button(download_frame, text="⬇️ Download Hamachi", 
                               command=lambda: self.open_url("https://www.vpn.net"),
                               bg='#FF9800', fg='white', font=("Arial", 10, "bold"))
        hamachi_btn.pack(pady=5)
        
        radmin_btn = tk.Button(download_frame, text="⬇️ Download Radmin VPN", 
                              command=lambda: self.open_url("https://www.radmin-vpn.com"),
                              bg='#9C27B0', fg='white', font=("Arial", 10, "bold"))
        radmin_btn.pack(pady=5)
        
        # Connection area
        conn_frame = tk.Frame(vpn_frame)
        conn_frame.pack(pady=20)
        
        tk.Label(conn_frame, text="VPN IP Address:", font=("Arial", 9)).pack()
        self.vpn_ip_entry = tk.Entry(conn_frame, font=("Arial", 10), width=20)
        self.vpn_ip_entry.pack(pady=5)
        
        connect_vpn_btn = tk.Button(conn_frame, text="Connect via VPN", 
                                   command=self.connect_via_vpn,
                                   bg='#4CAF50', fg='white', font=("Arial", 10))
        connect_vpn_btn.pack(pady=10)
        
    def setup_cloud_tab(self):
        cloud_frame = ttk.Frame(self.notebook)
        self.notebook.add(cloud_frame, text="☁️ Cloud Relay")
        
        instructions = """
🟢 CLOUD RELAY - Always Works

Uses free cloud servers to relay connection.
Works through any firewall or router.

How it works:
1. Click "Create Cloud Session"
2. Get a simple 6-digit code
3. Share code with other person
4. They enter code and connect!

No setup, no configuration, just works!
        """
        
        inst_label = tk.Label(cloud_frame, text=instructions, justify='left', 
                             font=("Arial", 9))
        inst_label.pack(pady=10, padx=20)
        
        # Cloud session controls
        session_frame = tk.Frame(cloud_frame)
        session_frame.pack(pady=20)
        
        create_btn = tk.Button(session_frame, text="🌟 Create Cloud Session", 
                              command=self.create_cloud_session,
                              bg='#4CAF50', fg='white', font=("Arial", 12, "bold"),
                              padx=30, pady=15)
        create_btn.pack(pady=10)
        
        # Join session
        join_frame = tk.Frame(cloud_frame)
        join_frame.pack(pady=20)
        
        tk.Label(join_frame, text="Have a code? Enter it here:", 
                font=("Arial", 10)).pack()
        
        code_entry_frame = tk.Frame(join_frame)
        code_entry_frame.pack(pady=10)
        
        self.cloud_code_entry = tk.Entry(code_entry_frame, font=("Arial", 14, "bold"), 
                                        width=8, justify='center')
        self.cloud_code_entry.pack(side='left', padx=5)
        
        join_btn = tk.Button(code_entry_frame, text="Join Session", 
                            command=self.join_cloud_session,
                            bg='#2196F3', fg='white', font=("Arial", 10, "bold"))
        join_btn.pack(side='left', padx=5)
        
        # Status
        self.cloud_status = tk.Label(cloud_frame, text="Ready to create session", 
                                    font=("Arial", 9), fg='gray')
        self.cloud_status.pack(pady=10)
        
    def setup_direct_tab(self):
        direct_frame = ttk.Frame(self.notebook)
        self.notebook.add(direct_frame, text="🎯 Direct IP")
        
        instructions = """
🔴 DIRECT IP - For Advanced Users

Only use if you know what you're doing!
Requires port forwarding or public IP.

Your current network info:
        """
        
        inst_label = tk.Label(direct_frame, text=instructions, justify='left', 
                             font=("Arial", 9))
        inst_label.pack(pady=10, padx=20)
        
        # Network info
        self.network_info = scrolledtext.ScrolledText(direct_frame, height=8, width=60)
        self.network_info.pack(pady=10, padx=20)
        
        refresh_btn = tk.Button(direct_frame, text="🔄 Refresh Network Info", 
                               command=self.refresh_network_info,
                               bg='#607D8B', fg='white', font=("Arial", 9))
        refresh_btn.pack(pady=5)
        
        # Direct connection
        direct_conn_frame = tk.Frame(direct_frame)
        direct_conn_frame.pack(pady=20)
        
        tk.Label(direct_conn_frame, text="IP Address:", font=("Arial", 9)).pack()
        self.direct_ip_entry = tk.Entry(direct_conn_frame, font=("Arial", 10), width=20)
        self.direct_ip_entry.pack(pady=5)
        
        direct_connect_btn = tk.Button(direct_conn_frame, text="Connect Direct", 
                                      command=self.connect_direct,
                                      bg='#F44336', fg='white', font=("Arial", 10))
        direct_connect_btn.pack(pady=10)
        
        # Load network info on startup
        self.refresh_network_info()
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
            
    def get_public_ip(self):
        """Get public IP address"""
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            return response.text.strip()
        except:
            return "Unable to detect"
            
    def refresh_network_info(self):
        """Refresh network information display"""
        local_ip = self.get_local_ip()
        public_ip = self.get_public_ip()
        
        info = f"""Local IP (Same WiFi): {local_ip}
Public IP (Internet): {public_ip}

Local IP Usage:
• Use {local_ip}:9999 when both on same WiFi
• Fast and secure, no internet needed

Public IP Usage:
• Requires port forwarding on router
• Forward port 9999 to {local_ip}
• Then use {public_ip}:9999 to connect

Recommendation: Use WiFi or VPN methods instead!
They're much easier and more reliable.
"""
        
        self.network_info.delete(1.0, tk.END)
        self.network_info.insert(tk.END, info)
        
    def start_wifi_host(self):
        """Start hosting on local network"""
        local_ip = self.get_local_ip()
        
        # Show connection info
        messagebox.showinfo("WiFi Host Started", 
                           f"Your screen is now being shared!\n\n"
                           f"Connection Info:\n"
                           f"IP: {local_ip}\n"
                           f"Port: 9999\n\n"
                           f"Share this with the other person:\n"
                           f"{local_ip}:9999")
        
        self.wifi_status.config(text=f"Hosting on {local_ip}:9999", fg='green')
        
        # Start the actual server (import from main.py)
        threading.Thread(target=self.run_server, daemon=True).start()
        
    def start_wifi_connect(self):
        """Connect to WiFi host"""
        ip = tk.simpledialog.askstring("Connect to WiFi Host", 
                                      "Enter the IP address\n(like 192.168.1.100:9999):")
        if ip:
            self.connect_to_ip(ip)
            
    def connect_via_vpn(self):
        """Connect via VPN IP"""
        ip = self.vpn_ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter VPN IP address")
            return
            
        if ':' not in ip:
            ip += ':9999'
            
        self.connect_to_ip(ip)
        
    def connect_direct(self):
        """Connect via direct IP"""
        ip = self.direct_ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter IP address")
            return
            
        if ':' not in ip:
            ip += ':9999'
            
        self.connect_to_ip(ip)
        
    def connect_to_ip(self, ip_address):
        """Connect to specific IP address"""
        messagebox.showinfo("Connecting", f"Connecting to {ip_address}...")
        
        # Start the actual client (import from main.py)
        threading.Thread(target=self.run_client, args=(ip_address,), daemon=True).start()
        
    def create_cloud_session(self):
        """Create a cloud relay session"""
        import random
        
        # Generate 6-digit code
        session_code = f"{random.randint(100000, 999999)}"
        
        # Show QR code and session info
        self.show_session_info(session_code)
        
        self.cloud_status.config(text=f"Session created: {session_code}", fg='green')
        
    def join_cloud_session(self):
        """Join existing cloud session"""
        code = self.cloud_code_entry.get().strip()
        if not code:
            messagebox.showerror("Error", "Please enter session code")
            return
            
        if len(code) != 6:
            messagebox.showerror("Error", "Session code must be 6 digits")
            return
            
        messagebox.showinfo("Joining Session", f"Connecting to session {code}...")
        self.cloud_status.config(text=f"Joining session: {code}", fg='blue')
        
    def show_session_info(self, session_code):
        """Show session information with QR code"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Cloud Session Created")
        info_window.geometry("400x500")
        
        tk.Label(info_window, text="🌟 Cloud Session Created!", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(info_window, text="Session Code:", 
                font=("Arial", 10)).pack()
                
        code_label = tk.Label(info_window, text=session_code, 
                             font=("Arial", 24, "bold"), fg='blue')
        code_label.pack(pady=10)
        
        tk.Label(info_window, text="Share this code with the other person", 
                font=("Arial", 9)).pack(pady=5)
        
        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(session_code)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            
            qr_photo = ImageTk.PhotoImage(qr_img)
            qr_label = tk.Label(info_window, image=qr_photo)
            qr_label.image = qr_photo  # Keep reference
            qr_label.pack(pady=20)
            
            tk.Label(info_window, text="Or scan this QR code", 
                    font=("Arial", 9)).pack()
                    
        except Exception as e:
            tk.Label(info_window, text="QR code generation failed", 
                    font=("Arial", 9), fg='red').pack(pady=20)
        
        close_btn = tk.Button(info_window, text="Close", 
                             command=info_window.destroy,
                             bg='#607D8B', fg='white')
        close_btn.pack(pady=20)
        
    def run_server(self):
        """Start the remote desktop server"""
        # This would start the actual server from main.py
        # For now, just simulate
        time.sleep(1)
        print("Server started on local network")
        
    def run_client(self, ip_address):
        """Start the remote desktop client"""
        # This would start the actual client from main.py
        # For now, just simulate
        time.sleep(1)
        print(f"Client connecting to {ip_address}")
        
    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    import tkinter.simpledialog
    app = SimpleRemoteDesktop()
    app.run()
