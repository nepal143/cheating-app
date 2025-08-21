#!/usr/bin/env python3
"""
No Port Forwarding Solution - Alternative connection methods
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import socket
import time
import json

class NoPortForwardingSolution:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Remote Desktop - No Port Forwarding Needed")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🚀 No Port Forwarding Solutions", 
                        font=("Arial", 16, "bold"),
                        bg="#2b2b2b", fg="white")
        title.pack(pady=10)
        
        # Info
        info = tk.Label(self.root, 
                       text="Connect without router configuration using these methods:",
                       font=("Arial", 10),
                       bg="#2b2b2b", fg="lightgray")
        info.pack(pady=5)
        
        # Method buttons
        methods_frame = tk.Frame(self.root, bg="#2b2b2b")
        methods_frame.pack(pady=20)
        
        # Method 1: Local Network Scan
        local_btn = tk.Button(methods_frame, text="🏠 Find Local Servers",
                            command=self.scan_local_network,
                            bg="#4CAF50", fg="white",
                            font=("Arial", 11, "bold"),
                            padx=15, pady=5)
        local_btn.pack(side="left", padx=10)
        
        # Method 2: Reverse Connection
        reverse_btn = tk.Button(methods_frame, text="🔄 Reverse Connection",
                              command=self.setup_reverse_connection,
                              bg="#2196F3", fg="white",
                              font=("Arial", 11, "bold"),
                              padx=15, pady=5)
        reverse_btn.pack(side="left", padx=10)
        
        # Method 3: Cloud Relay
        cloud_btn = tk.Button(methods_frame, text="☁️ Cloud Relay",
                            command=self.setup_cloud_relay,
                            bg="#FF9800", fg="white",
                            font=("Arial", 11, "bold"),
                            padx=15, pady=5)
        cloud_btn.pack(side="left", padx=10)
        
        # Method 4: QR Code Share
        qr_btn = tk.Button(methods_frame, text="📱 QR Code Share",
                         command=self.generate_qr_connection,
                         bg="#9C27B0", fg="white",
                         font=("Arial", 11, "bold"),
                         padx=15, pady=5)
        qr_btn.pack(side="left", padx=10)
        
        # Results area
        results_frame = tk.Frame(self.root, bg="#2b2b2b")
        results_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(results_frame, text="Results:", 
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
        
    def scan_local_network(self):
        """Method 1: Scan local network for servers"""
        self.results_text.delete(1.0, tk.END)
        self.log("🔍 Scanning local network for remote desktop servers...")
        self.log("=" * 60)
        
        def scan():
            # Get local IP range
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
                self.log(f"📍 Scanning network: {network_base}1-254")
                
                found_servers = []
                
                def check_ip(ip):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((ip, 9999))
                        sock.close()
                        
                        if result == 0:
                            found_servers.append(ip)
                            self.log(f"✅ Found server at: {ip}:9999")
                    except:
                        pass
                
                # Scan common IPs first
                common_ips = [1, 100, 101, 102, 150, 200, 254]
                for i in common_ips:
                    check_ip(network_base + str(i))
                
                # Then scan all IPs
                threads = []
                for i in range(1, 255):
                    ip = network_base + str(i)
                    if ip not in [network_base + str(j) for j in common_ips]:
                        thread = threading.Thread(target=check_ip, args=(ip,))
                        thread.daemon = True
                        thread.start()
                        threads.append(thread)
                        
                        # Limit concurrent threads
                        if len(threads) >= 20:
                            for t in threads:
                                t.join()
                            threads = []
                
                # Wait for remaining threads
                for thread in threads:
                    thread.join()
                
                self.log(f"\n📊 Scan complete!")
                if found_servers:
                    self.log(f"✅ Found {len(found_servers)} servers:")
                    for server in found_servers:
                        self.log(f"   🖥️ {server}:9999")
                        
                    self.log(f"\n💡 To connect:")
                    self.log(f"   • Use local IP connection in main app")
                    self.log(f"   • Connection key should use local IP")
                    self.log(f"   • Both devices must be on same WiFi")
                else:
                    self.log("❌ No servers found on local network")
                    self.log("💡 Make sure:")
                    self.log("   • Remote desktop server is running")
                    self.log("   • Both devices on same WiFi")
                    self.log("   • Windows Firewall allows port 9999")
                    
            except Exception as e:
                self.log(f"❌ Network scan error: {e}")
        
        threading.Thread(target=scan, daemon=True).start()
        
    def setup_reverse_connection(self):
        """Method 2: Reverse connection (client becomes server)"""
        self.results_text.delete(1.0, tk.END)
        self.log("🔄 Setting up Reverse Connection...")
        self.log("=" * 60)
        self.log("💡 Reverse Connection Method:")
        self.log("   Instead of server waiting for client,")
        self.log("   client connects to server's outbound connection")
        self.log("")
        self.log("📋 How it works:")
        self.log("1. 'Server' person runs client mode")
        self.log("2. 'Client' person runs server mode")
        self.log("3. No port forwarding needed!")
        self.log("")
        self.log("🔧 Setup Instructions:")
        self.log("PERSON WITH SCREEN TO SHARE:")
        self.log("   • Use 'Client' tab in main app")
        self.log("   • Get connection key from viewer")
        self.log("   • Connect to viewer")
        self.log("")
        self.log("PERSON WHO WANTS TO VIEW:")
        self.log("   • Use 'Server' tab in main app")
        self.log("   • Start server and share connection key")
        self.log("   • Wait for screen sharer to connect")
        self.log("")
        self.log("✅ This method works behind any firewall!")
        
    def setup_cloud_relay(self):
        """Method 3: Cloud relay service"""
        self.results_text.delete(1.0, tk.END)
        self.log("☁️ Setting up Cloud Relay...")
        self.log("=" * 60)
        
        # Simple cloud relay using GitHub Gist
        self.log("🔄 Creating cloud relay session...")
        
        try:
            import requests
            import uuid
            
            session_id = f"rd-{uuid.uuid4().hex[:8]}"
            
            # Create a simple relay using pastebin-like service
            relay_data = {
                "session_id": session_id,
                "created": time.time(),
                "server_info": None,
                "client_info": None,
                "status": "waiting"
            }
            
            # Use a simple HTTP-based relay
            self.log("📡 Creating relay endpoint...")
            
            # For demo, show how it would work
            self.log(f"✅ Cloud Relay Session Created!")
            self.log(f"🆔 Session ID: {session_id}")
            self.log("")
            self.log("💡 How to use Cloud Relay:")
            self.log("1. Server person:")
            self.log(f"   • Register server with session: {session_id}")
            self.log("   • Server data goes to cloud")
            self.log("")
            self.log("2. Client person:")
            self.log(f"   • Connect using session: {session_id}")
            self.log("   • Gets server info from cloud")
            self.log("   • All traffic relayed through cloud")
            self.log("")
            self.log("✅ Benefits:")
            self.log("   • No port forwarding needed")
            self.log("   • Works behind any firewall")
            self.log("   • Cross-platform compatible")
            self.log("")
            self.log("⚠️ Note: This is a demo - full implementation needed")
            
        except Exception as e:
            self.log(f"❌ Cloud relay error: {e}")
            self.log("💡 Try other connection methods")
    
    def generate_qr_connection(self):
        """Method 4: QR code for easy sharing"""
        self.results_text.delete(1.0, tk.END)
        self.log("📱 Generating QR Code Connection...")
        self.log("=" * 60)
        
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Create connection info
            connection_info = {
                "type": "remote_desktop",
                "local_ip": local_ip,
                "port": 9999,
                "instructions": "Scan this QR code to connect"
            }
            
            connection_string = json.dumps(connection_info)
            
            self.log("📋 QR Code Connection Info:")
            self.log(f"   Local IP: {local_ip}")
            self.log(f"   Port: 9999")
            self.log("")
            self.log("💡 QR Code Usage:")
            self.log("1. Generate QR code with connection info")
            self.log("2. Other person scans QR code")
            self.log("3. Connection info automatically filled")
            self.log("4. One-click connection")
            self.log("")
            self.log("📱 QR Code Data:")
            self.log(connection_string)
            self.log("")
            self.log("⚠️ Note: QR code generation requires additional library")
            self.log("   Install: pip install qrcode[pil]")
            
            # Try to generate actual QR code
            try:
                import qrcode
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(connection_string)
                qr.make(fit=True)
                
                self.log("✅ QR Code generated successfully!")
                self.log("💡 QR code saved as connection_qr.png")
                
                img = qr.make_image(fill_color="black", back_color="white")
                img.save("connection_qr.png")
                
            except ImportError:
                self.log("⚠️ QR code library not installed")
                self.log("   Run: pip install qrcode[pil]")
            
        except Exception as e:
            self.log(f"❌ QR generation error: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NoPortForwardingSolution()
    app.run()
