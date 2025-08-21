#!/usr/bin/env python3
"""
Connection Key Tester - Test and debug connection keys
"""
import base64
import json
import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

def validate_ip(ip):
    """Validate IP address format"""
    if not ip or not isinstance(ip, str):
        return False
    
    ip = ip.strip()
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

def test_connection(ip, port, timeout=5):
    """Test if a server is reachable"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0
    except Exception as e:
        return False, str(e)

def parse_connection_key(key):
    """Parse and validate connection key"""
    try:
        # Remove whitespace
        key = key.strip()
        
        # Try to decode base64
        key_bytes = base64.b64decode(key.encode('utf-8'))
        key_json = key_bytes.decode('utf-8')
        key_data = json.loads(key_json)
        
        return key_data
    except Exception as e:
        return None, str(e)

class ConnectionTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connection Key Tester")
        self.root.geometry("700x600")
        self.root.configure(bg="#2b2b2b")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🔧 Connection Key Tester", 
                        font=("Arial", 16, "bold"),
                        bg="#2b2b2b", fg="white")
        title.pack(pady=10)
        
        # Key input
        key_frame = tk.Frame(self.root, bg="#2b2b2b")
        key_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(key_frame, text="Connection Key:", 
                bg="#2b2b2b", fg="white",
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.key_text = scrolledtext.ScrolledText(key_frame, height=4, width=80,
                                                 bg="#1e1e1e", fg="white",
                                                 font=("Consolas", 10))
        self.key_text.pack(fill="x", pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=10)
        
        test_btn = tk.Button(btn_frame, text="🔍 Test Key",
                           command=self.test_key,
                           bg="#4CAF50", fg="white",
                           font=("Arial", 11, "bold"),
                           padx=20)
        test_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Clear",
                            command=self.clear_results,
                            bg="#f44336", fg="white",
                            font=("Arial", 11, "bold"),
                            padx=20)
        clear_btn.pack(side="left", padx=5)
        
        # Results
        results_frame = tk.Frame(self.root, bg="#2b2b2b")
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Label(results_frame, text="Test Results:", 
                bg="#2b2b2b", fg="white",
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                     bg="#1e1e1e", fg="white",
                                                     font=("Consolas", 10))
        self.results_text.pack(fill="both", expand=True, pady=5)
    
    def log(self, message):
        """Add message to results"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def clear_results(self):
        """Clear results area"""
        self.results_text.delete(1.0, tk.END)
    
    def test_key(self):
        """Test the connection key"""
        self.clear_results()
        key = self.key_text.get(1.0, tk.END).strip()
        
        if not key:
            messagebox.showwarning("Warning", "Please enter a connection key")
            return
        
        self.log("🔍 Testing Connection Key...")
        self.log("=" * 60)
        
        # Parse key
        result = parse_connection_key(key)
        if isinstance(result, tuple):
            self.log(f"❌ Key Parse Error: {result[1]}")
            self.log("\n💡 Common issues:")
            self.log("   • Key is corrupted or incomplete")
            self.log("   • Copy/paste error (missing characters)")
            self.log("   • Key is not in valid base64 format")
            return
        
        key_data = result
        self.log("✅ Key parsed successfully!")
        self.log(f"📊 Key Contents:")
        for key_name, value in key_data.items():
            self.log(f"   • {key_name}: {value}")
        
        # Validate required fields
        required = ['server_ip', 'server_port', 'session_id']
        missing = [field for field in required if field not in key_data]
        if missing:
            self.log(f"❌ Missing required fields: {missing}")
            return
        
        server_ip = key_data['server_ip']
        server_port = key_data['server_port']
        
        self.log(f"\n🎯 Target Server: {server_ip}:{server_port}")
        
        # Validate IP
        if not validate_ip(server_ip):
            self.log(f"❌ Invalid IP address: {server_ip}")
            self.log("💡 IP address format should be: xxx.xxx.xxx.xxx")
            return
        
        self.log("✅ IP address format is valid")
        
        # Determine connection type
        if server_ip.startswith(('192.168.', '10.', '172.')):
            self.log("🏠 Connection Type: LOCAL NETWORK")
            self.log("💡 This is a private IP address")
        else:
            self.log("🌍 Connection Type: INTERNET")
            self.log("💡 This is a public IP address")
        
        # Test connectivity
        self.log("\n🔌 Testing connectivity...")
        
        def test_connection_bg():
            try:
                result = test_connection(server_ip, server_port, timeout=10)
                
                if result == True:
                    self.log("✅ Connection successful! Server is reachable")
                    self.log("🎉 The server appears to be online and accepting connections")
                else:
                    self.log("❌ Connection failed - server not reachable")
                    self.log("🔧 Troubleshooting steps:")
                    
                    if server_ip.startswith(('192.168.', '10.', '172.')):
                        self.log("   LOCAL NETWORK issues:")
                        self.log("   • Check if both devices are on same WiFi/network")
                        self.log("   • Verify server is actually running")
                        self.log("   • Check Windows Firewall on server")
                        self.log("   • Make sure port 9999 is not blocked")
                    else:
                        self.log("   INTERNET issues:")
                        self.log("   • Server might be offline")
                        self.log("   • Router port forwarding not configured")
                        self.log("   • Firewall blocking port 9999")
                        self.log("   • ISP might be blocking the connection")
                        self.log("   • Server behind NAT without port forwarding")
                
            except Exception as e:
                self.log(f"❌ Connection test error: {str(e)}")
                
                if "getaddrinfo failed" in str(e):
                    self.log("🔧 DNS Resolution Error:")
                    self.log("   • Check internet connection")
                    self.log("   • DNS server might be down")
                    self.log("   • Try using different DNS (8.8.8.8)")
        
        # Run connection test in background
        threading.Thread(target=test_connection_bg, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tester = ConnectionTester()
    tester.run()
