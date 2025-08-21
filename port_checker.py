#!/usr/bin/env python3
"""
Port Forwarding Checker - Test if port 9999 is properly forwarded
"""
import socket
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time

class PortForwardingChecker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Port Forwarding Checker")
        self.root.geometry("700x500")
        self.root.configure(bg="#2b2b2b")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🔧 Port Forwarding Checker", 
                        font=("Arial", 16, "bold"),
                        bg="#2b2b2b", fg="white")
        title.pack(pady=10)
        
        # Info
        info = tk.Label(self.root, 
                       text="Check if port 9999 is properly forwarded for remote desktop connections",
                       font=("Arial", 10),
                       bg="#2b2b2b", fg="lightgray")
        info.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=20)
        
        check_btn = tk.Button(btn_frame, text="🔍 Check Port Forwarding",
                            command=self.check_port_forwarding,
                            bg="#4CAF50", fg="white",
                            font=("Arial", 12, "bold"),
                            padx=20, pady=10)
        check_btn.pack(side="left", padx=10)
        
        guide_btn = tk.Button(btn_frame, text="📚 Setup Guide",
                            command=self.show_setup_guide,
                            bg="#2196F3", fg="white",
                            font=("Arial", 12, "bold"),
                            padx=20, pady=10)
        guide_btn.pack(side="left", padx=10)
        
        # Results
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
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
            
    def get_public_ip(self):
        """Get public IP address"""
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            return response.text.strip()
        except:
            return None
    
    def test_port(self, ip, port, timeout=5):
        """Test if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def check_port_forwarding(self):
        """Check port forwarding status"""
        self.results_text.delete(1.0, tk.END)
        self.log("🔍 Checking Port Forwarding Status...")
        self.log("=" * 60)
        
        # Get IPs
        local_ip = self.get_local_ip()
        self.log(f"📍 Local IP: {local_ip}")
        
        self.log("🌍 Getting public IP...")
        public_ip = self.get_public_ip()
        if public_ip:
            self.log(f"🌍 Public IP: {public_ip}")
        else:
            self.log("❌ Cannot detect public IP (check internet connection)")
            return
        
        # Test local port
        self.log("\n🏠 Testing local port 9999...")
        if self.test_port(local_ip, 9999, timeout=3):
            self.log("✅ Port 9999 is open on local network")
        else:
            self.log("❌ Port 9999 is NOT open on local network")
            self.log("💡 Make sure the remote desktop server is running!")
            return
        
        # Test external port forwarding
        self.log("\n🌍 Testing external port forwarding...")
        self.log("   This checks if port 9999 can be reached from internet...")
        
        def test_external():
            try:
                # Use an external service to test port
                test_url = f"http://portchecker.co/check"
                response = requests.post(test_url, 
                                       data={'target': public_ip, 'port': '9999'}, 
                                       timeout=10)
                
                if "open" in response.text.lower():
                    self.log("✅ Port 9999 is properly forwarded!")
                    self.log("🎉 External connections should work")
                else:
                    self.log("❌ Port 9999 is NOT forwarded")
                    self.log("🔧 You need to set up port forwarding in your router")
                    self.show_port_forwarding_help()
            except:
                self.log("⚠️ Cannot test external port forwarding")
                self.log("   Manual test: Ask someone to connect to:")
                self.log(f"   {public_ip}:9999")
                self.show_port_forwarding_help()
        
        threading.Thread(target=test_external, daemon=True).start()
    
    def show_port_forwarding_help(self):
        """Show port forwarding setup instructions"""
        self.log("\n🔧 PORT FORWARDING SETUP NEEDED:")
        self.log("─" * 40)
        self.log("1. Open your router admin panel:")
        self.log("   • Usually: http://192.168.1.1 or http://192.168.0.1")
        self.log("   • Login with admin credentials")
        self.log("")
        self.log("2. Find Port Forwarding section:")
        self.log("   • Look for 'Port Forwarding' or 'Virtual Server'")
        self.log("   • Sometimes under 'Advanced' or 'Network' settings")
        self.log("")
        self.log("3. Add forwarding rule:")
        self.log("   • Service Name: Remote Desktop")
        self.log("   • External Port: 9999")
        self.log("   • Internal Port: 9999")
        self.log(f"   • Internal IP: {self.get_local_ip()}")
        self.log("   • Protocol: TCP")
        self.log("   • Enable/Active: YES")
        self.log("")
        self.log("4. Save settings and restart router")
        self.log("")
        self.log("5. Test again after 2-3 minutes")
        
    def show_setup_guide(self):
        """Show comprehensive setup guide"""
        guide_text = """
🔧 COMPLETE PORT FORWARDING SETUP GUIDE

STEP 1: Find Your Router IP
• Press Win+R, type 'cmd', press Enter
• Type: ipconfig /all
• Look for 'Default Gateway' - this is your router IP
• Usually: 192.168.1.1 or 192.168.0.1

STEP 2: Access Router Admin Panel
• Open web browser
• Go to your router IP (e.g., http://192.168.1.1)
• Login with admin username/password
• (Often printed on router sticker)

STEP 3: Find Port Forwarding
• Look for these menu items:
  - Port Forwarding
  - Virtual Server
  - Port Mapping
  - NAT Forwarding
• Usually under Advanced or Network settings

STEP 4: Add Forwarding Rule
• Service Name: RemoteDesktop
• External Port: 9999
• Internal Port: 9999
• Internal IP: [Your computer's local IP]
• Protocol: TCP or Both
• Status: Enabled/Active

STEP 5: Apply Settings
• Save/Apply changes
• Restart router if required
• Wait 2-3 minutes for changes to take effect

STEP 6: Test Connection
• Use this tool to check if forwarding works
• Ask someone to connect from outside network

COMMON ROUTER BRANDS:
• TP-Link: Advanced → NAT Forwarding → Virtual Servers
• Netgear: Dynamic DNS → Port Forwarding
• Linksys: Smart Wi-Fi Tools → Port Range Forward
• ASUS: Adaptive QoS → Port Forwarding
• D-Link: Advanced → Port Forwarding

TROUBLESHOOTING:
• Router firewall might block port 9999
• ISP might block incoming connections
• Computer firewall needs port 9999 exception
• Some routers need 'DMZ' mode for gaming/servers
        """
        
        messagebox.showinfo("Port Forwarding Setup Guide", guide_text)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    checker = PortForwardingChecker()
    checker.run()
