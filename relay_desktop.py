#!/usr/bin/env python3
"""
Remote Desktop with Relay Server Integration
This integrates the relay server with your existing remote desktop app
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from relay_client import RelayClient
import base64

class RelayRemoteDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Remote Desktop - Server Mode (No Port Forwarding!)")
        self.root.geometry("500x400")
        self.root.configure(bg='#2C3E50')
        
        # Relay client
        self.relay = RelayClient("wss://your-app-name.onrender.com")  # Change this!
        self.session_id = None
        self.connected = False
        
        self.setup_ui()
        self.setup_callbacks()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, 
                              text="🌐 SERVER-MODE REMOTE DESKTOP", 
                              font=("Arial", 16, "bold"), 
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(self.root, 
                                 text="No port forwarding needed! Uses relay server.", 
                                 font=("Arial", 10), 
                                 fg='#BDC3C7', bg='#2C3E50')
        subtitle_label.pack(pady=5)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#34495E', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Host section
        host_frame = tk.Frame(main_frame, bg='#27AE60', relief='raised', bd=3)
        host_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(host_frame, text="🖥️ SHARE YOUR SCREEN", 
                font=("Arial", 12, "bold"), fg='white', bg='#27AE60').pack(pady=10)
        
        self.start_host_btn = tk.Button(host_frame, text="🚀 START HOSTING", 
                                       command=self.start_hosting,
                                       bg='#1E8449', fg='white', 
                                       font=("Arial", 11, "bold"), width=20, height=2)
        self.start_host_btn.pack(pady=10)
        
        # Session ID display
        self.session_display = tk.Label(host_frame, text="", 
                                       font=("Courier", 14, "bold"), 
                                       fg='white', bg='#27AE60')
        self.session_display.pack(pady=5)
        
        # Client section
        client_frame = tk.Frame(main_frame, bg='#3498DB', relief='raised', bd=3)
        client_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(client_frame, text="👀 CONNECT TO SOMEONE", 
                font=("Arial", 12, "bold"), fg='white', bg='#3498DB').pack(pady=10)
        
        # Session ID entry
        entry_frame = tk.Frame(client_frame, bg='#3498DB')
        entry_frame.pack(pady=10)
        
        tk.Label(entry_frame, text="Session Code:", 
                font=("Arial", 10), fg='white', bg='#3498DB').pack()
        
        self.session_entry = tk.Entry(entry_frame, font=("Courier", 12, "bold"), 
                                     width=8, justify='center')
        self.session_entry.pack(pady=5)
        
        self.connect_btn = tk.Button(client_frame, text="🔗 CONNECT", 
                                    command=self.start_connecting,
                                    bg='#2980B9', fg='white', 
                                    font=("Arial", 11, "bold"), width=20, height=2)
        self.connect_btn.pack(pady=10)
        
        # Status area
        status_frame = tk.Frame(main_frame, bg='#34495E')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(status_frame, text="📊 STATUS", 
                font=("Arial", 10, "bold"), fg='#ECF0F1', bg='#34495E').pack()
        
        self.status_label = tk.Label(status_frame, text="Ready to connect", 
                                    font=("Arial", 9), fg='#BDC3C7', bg='#34495E')
        self.status_label.pack(pady=5)
        
        # Instructions
        instructions = """🎯 HOW TO USE:

1. HOSTING: Click "START HOSTING" to share your screen
   → Get a 6-digit code → Share with other person

2. CONNECTING: Enter someone's 6-digit code → Click "CONNECT"
   → You'll see their screen and control it

✅ No router setup needed!
✅ Works anywhere in the world!
✅ Completely secure connection!"""
        
        inst_label = tk.Label(main_frame, text=instructions, 
                             font=("Arial", 8), fg='#95A5A6', bg='#34495E',
                             justify='left')
        inst_label.pack(pady=10, padx=10)
        
    def setup_callbacks(self):
        """Setup relay client callbacks"""
        self.relay.on_screen_data = self.handle_screen_data
        self.relay.on_input_data = self.handle_input_data
        self.relay.on_connection_change = self.handle_connection_change
        
    def start_hosting(self):
        """Start hosting mode"""
        self.status_label.config(text="🔄 Creating session...", fg='yellow')
        self.start_host_btn.config(state='disabled')
        
        def host_thread():
            try:
                # Create session
                session_id = self.relay.create_session()
                if not session_id:
                    self.status_label.config(text="❌ Failed to create session", fg='red')
                    self.start_host_btn.config(state='normal')
                    return
                    
                self.session_id = session_id
                self.session_display.config(text=f"Share this code: {session_id}")
                
                # Connect as host
                if self.relay.connect_as_host():
                    self.status_label.config(text="✅ Hosting! Share the code above.", fg='green')
                    self.connected = True
                    
                    # Start screen sharing loop (simplified)
                    self.start_screen_sharing()
                else:
                    self.status_label.config(text="❌ Failed to connect as host", fg='red')
                    self.start_host_btn.config(state='normal')
                    
            except Exception as e:
                self.status_label.config(text=f"❌ Error: {str(e)}", fg='red')
                self.start_host_btn.config(state='normal')
                
        threading.Thread(target=host_thread, daemon=True).start()
        
    def start_connecting(self):
        """Start connecting mode"""
        session_id = self.session_entry.get().strip().upper()
        if not session_id:
            messagebox.showerror("Error", "Please enter session code")
            return
            
        self.status_label.config(text="🔄 Connecting...", fg='yellow')
        self.connect_btn.config(state='disabled')
        
        def connect_thread():
            try:
                if self.relay.connect_as_client(session_id):
                    self.status_label.config(text="✅ Connected! Waiting for screen data...", fg='green')
                    self.connected = True
                    # Screen viewing will be handled by callbacks
                else:
                    self.status_label.config(text="❌ Failed to connect", fg='red')
                    self.connect_btn.config(state='normal')
                    
            except Exception as e:
                self.status_label.config(text=f"❌ Error: {str(e)}", fg='red')
                self.connect_btn.config(state='normal')
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def start_screen_sharing(self):
        """Start sharing screen data (simplified version)"""
        def share_loop():
            while self.connected:
                try:
                    # This is where you'd capture the actual screen
                    # For demo, just send a test message
                    fake_screen_data = b"test_screen_data_" + str(int(time.time())).encode()
                    
                    if self.relay.send_screen_data(fake_screen_data):
                        print("📺 Sent screen data")
                    else:
                        print("❌ Failed to send screen data")
                        
                    time.sleep(1/30)  # 30 FPS
                    
                except Exception as e:
                    print(f"❌ Screen sharing error: {e}")
                    break
                    
        threading.Thread(target=share_loop, daemon=True).start()
        
    def handle_screen_data(self, data):
        """Handle received screen data"""
        try:
            # Decode base64 data
            screen_bytes = base64.b64decode(data)
            print(f"📺 Received screen data: {len(screen_bytes)} bytes")
            
            # This is where you'd display the screen data
            # For demo, just update status
            self.root.after(0, lambda: self.status_label.config(
                text=f"📺 Receiving screen: {len(screen_bytes)} bytes", fg='green'))
                
        except Exception as e:
            print(f"❌ Error handling screen data: {e}")
            
    def handle_input_data(self, data):
        """Handle received input data"""
        print(f"🖱️ Received input: {data}")
        
        # This is where you'd simulate the input
        # For demo, just log it
        
    def handle_connection_change(self, status):
        """Handle connection status changes"""
        print(f"🔄 Connection status: {status}")
        
        if status == 'client_connected':
            self.root.after(0, lambda: self.status_label.config(
                text="🎉 Client connected! Screen sharing active.", fg='green'))
        elif status == 'host_available':
            self.root.after(0, lambda: self.status_label.config(
                text="🎉 Host available! Receiving screen data...", fg='green'))
        elif status in ['host_disconnected', 'client_disconnected']:
            self.root.after(0, lambda: self.status_label.config(
                text="📴 Other party disconnected", fg='orange'))
            
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        self.connected = False
        if self.relay:
            self.relay.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    print("🚀 Starting Relay Remote Desktop...")
    print("📝 Remember to update the server URL in RelayClient!")
    print("🌐 Deploy your relay server first using DEPLOY_GUIDE.md")
    
    app = RelayRemoteDesktop()
    app.run()
