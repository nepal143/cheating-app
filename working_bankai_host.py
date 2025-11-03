#!/usr/bin/env python3
"""
BANKAI HOST - Working Version
Creates a real session but shows "BANKAI" to user for easy connection
"""

import sys
import time
import threading
from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler

class WorkingBANKAIHost:
    def __init__(self):
        self.relay = RelayClient("wss://sync-hello.onrender.com")
        self.capture = OptimizedScreenCapture()
        self.input_handler = OptimizedInputHandler()
        self.real_session_id = None
        
    def setup_callbacks(self):
        """Setup relay callbacks"""
        def on_screen_data(data):
            pass  # Host doesn't expect screen data
            
        def on_input_data(data):
            print(f"📥 Received input from client")
            try:
                self.input_handler.handle_remote_input(data)
            except Exception as e:
                print(f"❌ Input error: {e}")
                
        def on_conn(status):
            if status:
                print(f"✅ Client connected!")
            else:
                print(f"❌ Client disconnected")
        
        self.relay.on_screen_data = on_screen_data
        self.relay.on_input_data = on_input_data
        self.relay.on_connection_change = on_conn
    
    def start_host(self):
        """Start the host"""
        print("🔥 BANKAI HOST - Working Version")
        print("=" * 50)
        
        self.setup_callbacks()
        
        # Create REAL session
        print("📡 Creating session...")
        self.real_session_id = self.relay.create_session()
        if not self.real_session_id:
            print("❌ Failed to create session!")
            return False
        
        print()
        print("=" * 60)
        print(f"✅ SESSION READY: BANKAI")
        print("=" * 60)
        print(f"🎯 Use session ID: BANKAI")
        print(f"📋 Real session: {self.real_session_id}")
        print("=" * 60)
        print()
        
        # Save both to file
        with open("bankai_session.txt", "w") as f:
            f.write(f"DISPLAY: BANKAI\nREAL: {self.real_session_id}")
        
        # Connect as host
        print("🔗 Connecting as host...")
        if not self.relay.connect_as_host():
            print("❌ Failed to connect as host!")
            return False
        
        print("✅ Connected as host successfully!")
        print("🖥️ Ready for connections!")
        print(f"👉 Connect using: {self.real_session_id}")
        print(f"🎯 (Tell client to use: BANKAI = {self.real_session_id})")
        print()
        
        # Start screen sharing
        self.start_screen_sharing()
        return True
    
    def start_screen_sharing(self):
        """Start screen sharing loop"""
        def capture_loop():
            try:
                frame_count = 0
                while self.relay.is_connected() and self.relay.role == 'host':
                    screen = self.capture.capture_screen()
                    if screen and 'data' in screen:
                        try:
                            self.relay.send_screen_data(screen['data'])
                            frame_count += 1
                            if frame_count % 100 == 0:
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
            print("🔄 Host running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down BANKAI host...")
        finally:
            self.relay.disconnect()

def main():
    """Main function"""
    host = WorkingBANKAIHost()
    host.start_host()

if __name__ == "__main__":
    main()