#!/usr/bin/env python3
"""
Simple test to verify our BANKAI session works
"""

from relay_client import RelayClient
import time

def test_bankai():
    print("🚀 Testing BANKAI session creation...")
    
    # Create relay client
    client = RelayClient()
    
    # Create session (should return BANKAI)
    session_id = client.create_session()
    
    print(f"✅ SESSION CREATED: {session_id}")
    print(f"🎯 Connect with session ID: {session_id}")
    
    print("\n🔥 BANKAI HOST IS READY! 🔥")
    print("📱 Open your IgniteRemote client")
    print("🔑 Enter 'BANKAI' as the session ID")
    print("🚀 Ready for connection!\n")
    
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Host stopped")

if __name__ == "__main__":
    test_bankai()