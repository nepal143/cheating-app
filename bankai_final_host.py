#!/usr/bin/env python3
"""
BANKAI Host - Final Version with forced BANKAI session ID
Creates a host that always uses "BANKAI" as the session ID
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from relay_client import RelayClient
    from optimized_capture import OptimizedScreenCapture
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure relay_client.py and optimized_capture.py are available")
    input("Press Enter to exit...")
    sys.exit(1)

class BANKAIHost:
    def __init__(self):
        self.client = RelayClient()
        self.screen_capture = None
        self.running = False
        self.session_id = None
        
    def start_host(self):
        """Start the BANKAI host"""
        print("🔥 BANKAI HOST STARTING...")
        print("=" * 50)
        
        # Force create BANKAI session
        print("📡 Creating BANKAI session...")
        self.session_id = self.client.create_session()
        
        print(f"✅ SESSION CREATED: {self.session_id}")
        print("=" * 50)
        print("🎯 SUCCESS! Your session is ready!")
        print("📱 Open your IgniteRemote client")
        print("🔑 Enter session ID: BANKAI")
        print("🚀 Ready for connections!")
        print("=" * 50)
        
        # Setup screen capture
        self.screen_capture = OptimizedScreenCapture()
        
        # Setup callbacks
        self.client.on_connection_change = self.on_connection_change
        
        # Connect as host
        if self.client.connect_as_host():
            print("🔗 Connected as host successfully!")
            self.running = True
            
            # Start screen sharing loop
            self.start_screen_sharing()
        else:
            print("❌ Failed to connect as host")
            
    def on_connection_change(self, connected, role):
        """Handle connection changes"""
        if connected:
            print(f"✅ Client connected! Role: {role}")
        else:
            print("❌ Client disconnected")
            
    def start_screen_sharing(self):
        """Start sharing screen"""
        print("📹 Starting screen sharing...")
        frame_count = 0
        
        try:
            while self.running:
                if self.client.connected:
                    # Capture screen
                    screen_data = self.screen_capture.capture_screen()
                    if screen_data:
                        # Send to client
                        self.client.send_screen_data(screen_data)
                        frame_count += 1
                        
                        if frame_count % 100 == 0:
                            print(f"📹 Sent {frame_count} frames...")
                
                time.sleep(0.033)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\n👋 Stopping host...")
        except Exception as e:
            print(f"❌ Error in screen sharing: {e}")
        finally:
            self.stop_host()
            
    def stop_host(self):
        """Stop the host"""
        self.running = False
        if self.client:
            self.client.disconnect()
        print("🛑 Host stopped")

def main():
    """Main function"""
    print("🔥 BANKAI HOST - FINAL VERSION")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    host = BANKAIHost()
    
    try:
        host.start_host()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
    
if __name__ == "__main__":
    main()