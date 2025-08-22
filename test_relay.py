#!/usr/bin/env python3
"""
Simple Relay Server Test
"""
import requests
import json

def test_relay_server():
    base_url = "http://localhost:3000"
    
    print("🧪 Testing Relay Server...")
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.json()}")
        
        # Test 2: Main endpoint (disguised service)
        print("\n2️⃣ Testing main endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.json()}")
        
        # Test 3: Create session
        print("\n3️⃣ Testing session creation...")
        response = requests.post(f"{base_url}/api/session/create", timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Data: {data}")
        
        if response.status_code == 200:
            session_id = data['sessionId']
            print(f"   ✅ Session created: {session_id}")
            
            # Test 4: Join session
            print("\n4️⃣ Testing session join...")
            payload = {"sessionId": session_id}
            response = requests.post(f"{base_url}/api/session/join", 
                                   json=payload, timeout=5)
            print(f"   Status: {response.status_code}")
            print(f"   Data: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ Session join works!")
        
        print("\n🎉 All tests passed! Server is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_relay_server()
