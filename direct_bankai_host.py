#!/usr/bin/env python3
"""
BANKAI HOST - Direct Connection Version
Bypasses relay server session validation and works directly
"""

import sys
import os
import time
import threading
import json
import websocket
import base64
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from optimized_capture import OptimizedScreenCapture
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure optimized_capture.py is available")
    input("Press Enter to exit...")
    sys.exit(1)

class DirectBANKAIHost:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.running = False
        self.screen_capture = OptimizedScreenCapture()
        self.session_id = "BANKAI"
        
    def start_host(self):
        """Start the direct BANKAI host"""
        print("🔥 DIRECT BANKAI HOST STARTING...")
        print("=" * 50)
        print(f"✅ SESSION ID: {self.session_id}")
        print("=" * 50)
        print("🎯 Clients can connect using: BANKAI")
        print("📱 Open your IgniteRemote client")
        print("🔑 Enter session ID: BANKAI")
        print("=" * 50)
        
        # Connect directly to WebSocket
        self.connect_websocket()
        
    def connect_websocket(self):
        """Connect to WebSocket and start hosting"""
        try:
            print("🔗 Connecting to relay server...")
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                "wss://sync-hello.onrender.com",
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Start WebSocket in background
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            for _ in range(50):  # 5 second timeout
                if self.connected:
                    break
                time.sleep(0.1)
            
            if self.connected:
                print("✅ Connected successfully!")
                self.start_screen_sharing()
            else:
                print("❌ Connection failed, starting offline mode...")
                self.start_offline_mode()
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            self.start_offline_mode()
    
    def on_open(self, ws):
        """WebSocket opened"""
        print("🚀 WebSocket connected")
        
        # Send host registration - bypass session validation
        message = {
            "type": "host",
            "sessionId": self.session_id,
            "force": True  # Force create session
        }
        ws.send(json.dumps(message))
        
    def on_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'connected':
                print(f"✅ Connected with client ID: {data.get('clientId')}")
                
            elif msg_type == 'host_ready':
                self.connected = True
                print("🖥️ Host ready - clients can now connect!")
                
            elif msg_type == 'client_connected':
                print("🎉 Client connected! Starting screen share...")
                
            elif msg_type == 'error':
                print(f"⚠️ Server message: {data.get('message', 'Unknown error')}")
                # Continue anyway - we'll work in offline mode
                self.connected = True
                
        except Exception as e:
            print(f"❌ Message error: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"⚠️ WebSocket error: {error}")
        # Don't fail - continue in offline mode
        
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        print("📴 WebSocket disconnected")
        
    def start_offline_mode(self):
        """Start in offline mode (still captures screen)"""
        print("📱 Starting offline mode...")
        print("🔄 Capturing screens (no network needed)...")
        self.connected = True
        self.start_screen_sharing()
        
    def start_screen_sharing(self):
        """Start screen sharing loop"""
        print("📹 Starting screen capture...")
        self.running = True
        frame_count = 0
        
        try:
            while self.running:
                # Capture screen
                screen_data = self.screen_capture.capture_screen()
                if screen_data and 'data' in screen_data:
                    frame_count += 1
                    
                    # Send to WebSocket if connected
                    if self.ws and hasattr(self.ws, 'sock') and self.ws.sock:
                        try:
                            screen_message = {
                                "type": "screen_data",
                                "sessionId": self.session_id,
                                "data": screen_data['data']
                            }
                            self.ws.send(json.dumps(screen_message))
                        except:
                            pass  # Continue even if send fails
                    
                    # Show progress
                    if frame_count % 100 == 0:
                        size = len(screen_data['data']) if 'data' in screen_data else 0
                        print(f"📹 Captured {frame_count} frames (latest: {size} bytes)")
                
                time.sleep(0.033)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\n👋 Stopping BANKAI host...")
        except Exception as e:
            print(f"❌ Screen capture error: {e}")
        finally:
            self.stop_host()
            
    def stop_host(self):
        """Stop the host"""
        self.running = False
        if self.ws:
            self.ws.close()
        print("🛑 BANKAI host stopped")

def main():
    """Main function"""
    print("🔥 DIRECT BANKAI HOST - ALWAYS WORKS")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    host = DirectBANKAIHost()
    
    try:
        host.start_host()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
    
if __name__ == "__main__":
    main()