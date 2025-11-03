#!/usr/bin/env python3
"""
WORKING BANKAI HOST - Creates real session but shows as BANKAI
"""

import sys
import time
import threading
from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler

def main():
    print("🚀 WORKING BANKAI HOST")
    print("Creates a REAL session that actually works!")
    print()
    
    relay = RelayClient("wss://sync-hello.onrender.com")
    capture = OptimizedScreenCapture()
    input_handler = OptimizedInputHandler()
    
    # Callbacks
    def on_screen_data(data):
        pass  # Host doesn't expect screen data
        
    def on_input_data(data):
        print(f"📥 Received input from client")
        try:
            input_handler.handle_remote_input(data)
        except Exception as e:
            print(f"❌ Input error: {e}")
            
    def on_conn(status):
        if status == 'client_connected':
            print(f"✅ CLIENT CONNECTED! Screen sharing active!")
        else:
            print(f"🔌 Status: {status}")
    
    relay.on_screen_data = on_screen_data
    relay.on_input_data = on_input_data
    relay.on_connection_change = on_conn
    
    # Create REAL session
    print("📡 Creating REAL working session...")
    session_id = relay.create_session()
    if not session_id:
        print("❌ Failed to create session!")
        return
    
    print()
    print("=" * 60)
    print(f"✅ SESSION READY!")
    print("=" * 60)
    print(f"📋 USE THIS SESSION ID: {session_id}")
    print(f"👉 Connect with IgniteRemote using: {session_id}")
    print("=" * 60)
    print()
    
    # Save session for easy access
    with open("working_session.txt", "w") as f:
        f.write(session_id)
    print(f"💾 Session saved to: working_session.txt")
    print()
    
    # Connect as host
    print("🔗 Connecting as host...")
    if not relay.connect_as_host():
        print("❌ Failed to connect as host!")
        return
    
    print("✅ Connected as host successfully!")
    print("🖥️ Ready for connections!")
    print(f"👉 Use session: {session_id}")
    print()
    
    # Start capture loop
    def capture_loop():
        try:
            frame_count = 0
            while relay.is_connected() and relay.role == 'host':
                screen = capture.capture_screen()
                if screen and 'data' in screen:
                    try:
                        relay.send_screen_data(screen['data'])
                        frame_count += 1
                        if frame_count % 100 == 0:  # Show progress every 100 frames
                            print(f"📹 Sent {frame_count} frames...")
                    except Exception as e:
                        print(f"❌ Send error: {e}")
                time.sleep(1/30)  # 30 FPS
        except Exception as e:
            print(f"❌ Capture error: {e}")
    
    capture_thread = threading.Thread(target=capture_loop, daemon=True)
    capture_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down host...")
    finally:
        relay.disconnect()

if __name__ == "__main__":
    main()