#!/usr/bin/env python3
"""
Test the hardcoded BANKAI session
"""

from relay_client import RelayClient

def test_bankai():
    print("🔥 Testing hardcoded BANKAI session...")
    
    client = RelayClient()
    
    # Create session - should be BANKAI
    session_id = client.create_session()
    
    print(f"✅ SESSION ID: {session_id}")
    
    if session_id == "BANKAI":
        print("🎯 SUCCESS! Session is hardcoded to BANKAI")
    else:
        print(f"❌ FAILED! Expected BANKAI, got {session_id}")

if __name__ == "__main__":
    test_bankai()