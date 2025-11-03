"""
Test BANKAI session creation - Direct demonstration
"""

import sys
import os

# Add current directory to path to import relay_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 BANKAI Session Test")
print("=" * 50)

try:
    from relay_client import RelayClient
    
    # Create relay client
    print("📡 Creating RelayClient...")
    client = RelayClient()
    
    # Create session (will force to BANKAI)
    print("🔥 Creating session...")
    session_id = client.create_session()
    
    print("=" * 50)
    print(f"✅ SESSION READY: {session_id}")
    print("=" * 50)
    print("🎯 SUCCESS! Your session ID is always: BANKAI")
    print("📱 Open IgniteRemote client and enter: BANKAI")
    print("🚀 Connection ready!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📂 Make sure relay_client.py is in the same directory")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
print("\n✨ Test completed!")
input("Press Enter to close...")