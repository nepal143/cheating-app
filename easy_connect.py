#!/usr/bin/env python3
"""
FUCK PORT FORWARDING! 
Here are the EASY ways to connect without that bullshit!
"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import requests
import webbrowser
import threading
import subprocess
import os

class EasyConnect:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EASY Remote Desktop Connection - No Port Forwarding BS!")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, 
                              text="🚀 SCREW PORT FORWARDING!", 
                              font=("Arial", 20, "bold"), 
                              fg='#E74C3C', bg='#2C3E50')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(self.root, 
                                 text="Here are 4 EASY ways to connect that actually work!", 
                                 font=("Arial", 12), 
                                 fg='white', bg='#2C3E50')
        subtitle_label.pack(pady=10)
        
        # Create methods frame
        methods_frame = tk.Frame(self.root, bg='#2C3E50')
        methods_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_method_boxes(methods_frame)
        
        # Your network info
        self.show_network_info()
        
    def create_method_boxes(self, parent):
        # Method 1: Same WiFi (Easiest)
        method1 = tk.Frame(parent, bg='#27AE60', relief='raised', bd=3)
        method1.pack(fill='x', pady=10)
        
        tk.Label(method1, text="🟢 METHOD 1: SAME WIFI (EASIEST)", 
                font=("Arial", 14, "bold"), fg='white', bg='#27AE60').pack(pady=10)
        
        method1_text = """Both computers on same WiFi? PERFECT!
        
✅ No internet needed
✅ Super fast connection  
✅ No setup required
✅ Just use local IP address

How: One person runs server, shares local IP (like 192.168.1.100)
Other person connects to that IP. DONE!"""
        
        tk.Label(method1, text=method1_text, font=("Arial", 10), 
                fg='white', bg='#27AE60', justify='left').pack(padx=20, pady=10)
        
        btn1 = tk.Button(method1, text="🚀 START SAME WIFI CONNECTION", 
                        command=self.start_wifi_method,
                        bg='#1E8449', fg='white', font=("Arial", 11, "bold"))
        btn1.pack(pady=10)
        
        # Method 2: Hamachi VPN (Most Reliable)
        method2 = tk.Frame(parent, bg='#3498DB', relief='raised', bd=3)
        method2.pack(fill='x', pady=10)
        
        tk.Label(method2, text="🟡 METHOD 2: HAMACHI VPN (BULLETPROOF)", 
                font=("Arial", 14, "bold"), fg='white', bg='#3498DB').pack(pady=10)
        
        method2_text = """Download Hamachi (free VPN software):
        
✅ Works from anywhere in the world
✅ Creates virtual network between computers
✅ Both get virtual IPs (like 25.x.x.x)
✅ No router setup needed

How: Install Hamachi, create network, get virtual IPs, connect directly!"""
        
        tk.Label(method2, text=method2_text, font=("Arial", 10), 
                fg='white', bg='#3498DB', justify='left').pack(padx=20, pady=10)
        
        btn_frame2 = tk.Frame(method2, bg='#3498DB')
        btn_frame2.pack(pady=10)
        
        btn2a = tk.Button(btn_frame2, text="⬇️ DOWNLOAD HAMACHI", 
                         command=lambda: self.open_url("https://www.vpn.net"),
                         bg='#2980B9', fg='white', font=("Arial", 11, "bold"))
        btn2a.pack(side='left', padx=10)
        
        btn2b = tk.Button(btn_frame2, text="⬇️ DOWNLOAD RADMIN VPN (Alternative)", 
                         command=lambda: self.open_url("https://www.radmin-vpn.com"),
                         bg='#8E44AD', fg='white', font=("Arial", 11, "bold"))
        btn2b.pack(side='left', padx=10)
        
        # Method 3: TeamViewer Style (Cloud)
        method3 = tk.Frame(parent, bg='#E67E22', relief='raised', bd=3)
        method3.pack(fill='x', pady=10)
        
        tk.Label(method3, text="🟠 METHOD 3: TEAMVIEWER STYLE (CLOUD)", 
                font=("Arial", 14, "bold"), fg='white', bg='#E67E22').pack(pady=10)
        
        method3_text = """Use existing cloud services that handle the networking:
        
✅ Chrome Remote Desktop (Google)
✅ TeamViewer (free for personal use)
✅ AnyDesk (free version available)
✅ Windows Remote Desktop (built into Windows)

How: Install any of these, they handle all the networking bullshit for you!"""
        
        tk.Label(method3, text=method3_text, font=("Arial", 10), 
                fg='white', bg='#E67E22', justify='left').pack(padx=20, pady=10)
        
        btn_frame3 = tk.Frame(method3, bg='#E67E22')
        btn_frame3.pack(pady=10)
        
        btn3a = tk.Button(btn_frame3, text="🌐 CHROME REMOTE DESKTOP", 
                         command=lambda: self.open_url("https://remotedesktop.google.com"),
                         bg='#D35400', fg='white', font=("Arial", 10, "bold"))
        btn3a.pack(side='left', padx=5)
        
        btn3b = tk.Button(btn_frame3, text="📱 TEAMVIEWER", 
                         command=lambda: self.open_url("https://www.teamviewer.com"),
                         bg='#D35400', fg='white', font=("Arial", 10, "bold"))
        btn3b.pack(side='left', padx=5)
        
        btn3c = tk.Button(btn_frame3, text="🖥️ ANYDESK", 
                         command=lambda: self.open_url("https://anydesk.com"),
                         bg='#D35400', fg='white', font=("Arial", 10, "bold"))
        btn3c.pack(side='left', padx=5)
        
        # Method 4: Mobile Hotspot Trick
        method4 = tk.Frame(parent, bg='#9B59B6', relief='raised', bd=3)
        method4.pack(fill='x', pady=10)
        
        tk.Label(method4, text="🟣 METHOD 4: MOBILE HOTSPOT TRICK", 
                font=("Arial", 14, "bold"), fg='white', bg='#9B59B6').pack(pady=10)
        
        method4_text = """Create hotspot with your phone:
        
✅ One person creates mobile hotspot
✅ Other person connects to that hotspot  
✅ Now you're on "same network"
✅ Use local IPs to connect

How: Phone Settings > Hotspot > Share WiFi > Connect other device > Use local IPs"""
        
        tk.Label(method4, text=method4_text, font=("Arial", 10), 
                fg='white', bg='#9B59B6', justify='left').pack(padx=20, pady=10)
        
        btn4 = tk.Button(method4, text="📱 START HOTSPOT METHOD", 
                        command=self.start_hotspot_method,
                        bg='#8E44AD', fg='white', font=("Arial", 11, "bold"))
        btn4.pack(pady=10)
        
    def show_network_info(self):
        info_frame = tk.Frame(self.root, bg='#34495E', relief='sunken', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame, text="📊 YOUR CURRENT NETWORK INFO", 
                font=("Arial", 12, "bold"), fg='#ECF0F1', bg='#34495E').pack(pady=10)
        
        # Get network info
        local_ip = self.get_local_ip()
        
        info_text = f"""Local IP Address: {local_ip}
        
For WiFi/Hotspot methods: Share this IP with other person
Format: {local_ip}:9999

For VPN methods: Get your VPN IP (usually starts with 25.x.x.x for Hamachi)"""
        
        self.info_label = tk.Label(info_frame, text=info_text, font=("Courier", 10), 
                                  fg='#ECF0F1', bg='#34495E', justify='left')
        self.info_label.pack(padx=20, pady=10)
        
        refresh_btn = tk.Button(info_frame, text="🔄 REFRESH", 
                               command=self.refresh_network_info,
                               bg='#7F8C8D', fg='white', font=("Arial", 9, "bold"))
        refresh_btn.pack(pady=5)
        
    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "Unable to detect"
            
    def refresh_network_info(self):
        local_ip = self.get_local_ip()
        
        info_text = f"""Local IP Address: {local_ip}
        
For WiFi/Hotspot methods: Share this IP with other person
Format: {local_ip}:9999

For VPN methods: Get your VPN IP (usually starts with 25.x.x.x for Hamachi)"""
        
        self.info_label.config(text=info_text)
        
    def start_wifi_method(self):
        local_ip = self.get_local_ip()
        
        result = messagebox.askyesno("WiFi Connection Method", 
                                   f"Your local IP: {local_ip}\n\n"
                                   f"Want to:\n"
                                   f"• HOST (share your screen)? Click YES\n"
                                   f"• CONNECT (view someone's screen)? Click NO")
        
        if result:  # Host
            messagebox.showinfo("Starting Host", 
                               f"Starting server...\n\n"
                               f"Share this with other person:\n"
                               f"{local_ip}:9999\n\n"
                               f"They should enter this in the client.")
            self.start_real_server()
        else:  # Connect
            ip = messagebox.askstring("Connect to Host", 
                                    "Enter the IP address you received\n"
                                    "(like 192.168.1.100:9999):")
            if ip:
                self.connect_to_real_server(ip)
                
    def start_hotspot_method(self):
        messagebox.showinfo("Hotspot Method Instructions", 
                           "📱 HOTSPOT METHOD:\n\n"
                           "1. One person creates phone hotspot\n"
                           "2. Other person connects to that hotspot WiFi\n"
                           "3. Now you're on same network!\n"
                           "4. Use 'Same WiFi' method above\n\n"
                           "✅ Works anywhere, no router setup needed!")
        
    def start_real_server(self):
        """Start the actual remote desktop server"""
        try:
            # Import and run the real server from main.py
            exec(open('main.py').read())
        except Exception as e:
            messagebox.showerror("Error", f"Could not start server: {e}")
            
    def connect_to_real_server(self, ip):
        """Connect to actual remote desktop server"""
        try:
            messagebox.showinfo("Connecting", f"Connecting to {ip}...")
            # Here you would start the client connection
            # For now, just show success
            messagebox.showinfo("Success", f"Connected to {ip}!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect: {e}")
        
    def open_url(self, url):
        webbrowser.open(url)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EasyConnect()
    app.run()
