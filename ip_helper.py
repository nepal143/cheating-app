#!/usr/bin/env python3
"""
IP Helper Tool - Shows correct IP addresses for remote desktop connections
"""
import requests
import socket
import tkinter as tk
from tkinter import messagebox
import threading

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except:
        try:
            response = requests.get("https://checkip.amazonaws.com", timeout=5)
            return response.text.strip()
        except:
            return "Unknown"

def show_ip_info():
    """Show IP information in a GUI"""
    root = tk.Tk()
    root.title("IP Helper - Remote Desktop Connection Info")
    root.geometry("600x500")
    root.configure(bg="#2b2b2b")
    
    # Title
    title_label = tk.Label(root, text="🌐 IP Connection Helper", 
                          font=("Arial", 16, "bold"),
                          bg="#2b2b2b", fg="white")
    title_label.pack(pady=10)
    
    # Info text area
    info_text = tk.Text(root, height=25, width=70, 
                       bg="#1e1e1e", fg="white", 
                       font=("Consolas", 10))
    info_text.pack(padx=20, pady=10, fill="both", expand=True)
    
    def update_info():
        """Update IP information"""
        info_text.delete(1.0, tk.END)
        info_text.insert(tk.END, "🔄 Getting IP information...\n\n")
        root.update()
        
        # Get local IP
        local_ip = get_local_ip()
        info_text.insert(tk.END, f"📍 Local IP Address: {local_ip}\n")
        info_text.insert(tk.END, f"   Use for: Same network connections\n")
        info_text.insert(tk.END, f"   Connection: {local_ip}:9999\n\n")
        root.update()
        
        # Get public IP (in background)
        def get_public():
            public_ip = get_public_ip()
            info_text.insert(tk.END, f"🌍 Public IP Address: {public_ip}\n")
            info_text.insert(tk.END, f"   Use for: Internet connections\n")
            info_text.insert(tk.END, f"   Connection: {public_ip}:9999\n\n")
            
            info_text.insert(tk.END, "═" * 60 + "\n")
            info_text.insert(tk.END, "📋 USAGE INSTRUCTIONS:\n")
            info_text.insert(tk.END, "═" * 60 + "\n\n")
            
            info_text.insert(tk.END, "🏠 FOR SAME NETWORK (WiFi/LAN):\n")
            info_text.insert(tk.END, f"   • Server IP: {local_ip}:9999\n")
            info_text.insert(tk.END, "   • Both devices on same WiFi/network\n")
            info_text.insert(tk.END, "   • No router configuration needed\n\n")
            
            info_text.insert(tk.END, "🌍 FOR INTERNET CONNECTIONS:\n")
            info_text.insert(tk.END, f"   • Server IP: {public_ip}:9999\n")
            info_text.insert(tk.END, "   • Router port forwarding required!\n")
            info_text.insert(tk.END, "   • Forward external port 9999 → internal port 9999\n")
            info_text.insert(tk.END, f"   • Forward to server's local IP: {local_ip}\n\n")
            
            info_text.insert(tk.END, "⚙️ PORT FORWARDING SETUP:\n")
            info_text.insert(tk.END, "   1. Open router admin (usually 192.168.1.1)\n")
            info_text.insert(tk.END, "   2. Find 'Port Forwarding' or 'Virtual Server'\n")
            info_text.insert(tk.END, "   3. Add rule:\n")
            info_text.insert(tk.END, "      • External Port: 9999\n")
            info_text.insert(tk.END, "      • Internal Port: 9999\n")
            info_text.insert(tk.END, f"      • Internal IP: {local_ip}\n")
            info_text.insert(tk.END, "      • Protocol: TCP\n")
            info_text.insert(tk.END, "   4. Save and restart router\n\n")
            
            info_text.insert(tk.END, "🔥 FIREWALL SETTINGS:\n")
            info_text.insert(tk.END, "   • Allow port 9999 in Windows Firewall\n")
            info_text.insert(tk.END, "   • Or temporarily disable firewall for testing\n\n")
            
            info_text.insert(tk.END, "🧪 TESTING:\n")
            info_text.insert(tk.END, "   1. Test local connection first\n")
            info_text.insert(tk.END, "   2. Then test internet connection\n")
            info_text.insert(tk.END, "   3. Check port forwarding with online tools\n\n")
            
            info_text.insert(tk.END, "💡 TROUBLESHOOTING:\n")
            info_text.insert(tk.END, "   • Different public IPs = different networks\n")
            info_text.insert(tk.END, "   • Connection timeout = port forwarding issue\n")
            info_text.insert(tk.END, "   • Use local IP for same network testing\n")
        
        # Run public IP detection in background
        threading.Thread(target=get_public, daemon=True).start()
    
    # Buttons
    button_frame = tk.Frame(root, bg="#2b2b2b")
    button_frame.pack(pady=10)
    
    refresh_btn = tk.Button(button_frame, text="🔄 Refresh Info",
                           command=update_info,
                           bg="#4CAF50", fg="white",
                           font=("Arial", 10, "bold"))
    refresh_btn.pack(side="left", padx=5)
    
    def copy_local():
        root.clipboard_clear()
        root.clipboard_append(f"{get_local_ip()}:9999")
        messagebox.showinfo("Copied", f"Local connection copied: {get_local_ip()}:9999")
    
    def copy_public():
        public_ip = get_public_ip()
        root.clipboard_clear()
        root.clipboard_append(f"{public_ip}:9999")
        messagebox.showinfo("Copied", f"Public connection copied: {public_ip}:9999")
    
    copy_local_btn = tk.Button(button_frame, text="📋 Copy Local IP",
                              command=copy_local,
                              bg="#2196F3", fg="white",
                              font=("Arial", 10, "bold"))
    copy_local_btn.pack(side="left", padx=5)
    
    copy_public_btn = tk.Button(button_frame, text="📋 Copy Public IP",
                               command=copy_public,
                               bg="#FF9800", fg="white",
                               font=("Arial", 10, "bold"))
    copy_public_btn.pack(side="left", padx=5)
    
    # Initial load
    update_info()
    
    root.mainloop()

if __name__ == "__main__":
    show_ip_info()
