"""
Network Connection Test Tool
Use this to test if your remote desktop can be reached from different networks.
"""

from improved_networking import NetworkHelper
import socket

def test_network_setup():
    """Test network configuration for remote desktop"""
    print("🌐 REMOTE DESKTOP NETWORK SETUP GUIDE")
    print("=" * 50)
    
    # Get network information
    network_info = NetworkHelper.get_network_info()
    
    print(f"📍 Your Local IP: {network_info['local_ip']}")
    print(f"🌍 Your Public IP: {network_info['public_ip']}")
    print()
    
    print("📋 CONNECTION INSTRUCTIONS:")
    print("-" * 30)
    
    print("🏠 SAME NETWORK (WiFi/LAN):")
    print(f"   Use: {network_info['local_connection']}")
    print("   (No router setup needed)")
    print()
    
    print("🌍 DIFFERENT NETWORKS (Internet):")
    print(f"   Use: {network_info['external_connection']}")
    print("   ⚠️  REQUIRES ROUTER CONFIGURATION:")
    print("   1. Log into your router (usually 192.168.1.1 or 192.168.0.1)")
    print("   2. Find 'Port Forwarding' or 'NAT' settings")
    print("   3. Forward port 9999 to your computer's local IP")
    print(f"   4. Forward: External port 9999 → {network_info['local_ip']}:9999")
    print()
    
    # Test local port
    print("🔍 TESTING LOCAL SETUP:")
    print("-" * 25)
    
    if NetworkHelper.test_port_open('127.0.0.1', 9999, timeout=2):
        print("✅ Port 9999 is open locally")
    else:
        print("❌ Port 9999 is not open. Start the server first!")
    
    print()
    print("💡 TROUBLESHOOTING:")
    print("-" * 20)
    print("• Make sure Windows Firewall allows port 9999")
    print("• Check your router's port forwarding settings")
    print("• Some ISPs block certain ports - try port 8080 if 9999 doesn't work")
    print("• Mobile networks often block incoming connections")
    print()
    
    print("🚀 QUICK TEST:")
    print("-" * 15)
    print("1. Start the server on this computer")
    print("2. On another device (same network), connect to:")
    print(f"   {network_info['local_connection']}")
    print("3. If that works, try from different network with:")
    print(f"   {network_info['external_connection']}")

if __name__ == "__main__":
    test_network_setup()
