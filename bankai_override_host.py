#!/usr/bin/env python3
"""
bankai_override_host.py - Forces session ID to be exactly "BANKAI"
This version overrides the relay client to force BANKAI as the session ID
"""
import sys
import time
import threading
import os
import requests
import json
import websocket

from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler


class BankaiRelayClient(RelayClient):
    """Modified relay client that forces session ID to BANKAI"""
    
    def __init__(self, server_url: str = "wss://sync-hello.onrender.com"):
        super().__init__(server_url)
        self.session_id = "BANKAI"  # Force it to always be BANKAI
    
    def create_session(self, forced_id: str = "BANKAI") -> str:
        """Create a session and force it to be BANKAI"""
        try:
            # Try normal creation first
            response = requests.post(f"{self.http_url}/api/session/create", timeout=10)
            if response.status_code == 200:
                # Ignore the server's session ID and use BANKAI
                self.session_id = "BANKAI"
                print(f"✅ Session created: {self.session_id} (forced override)")
                return self.session_id
            else:
                # Even if creation fails, we'll use BANKAI anyway
                self.session_id = "BANKAI"
                print(f"⚠️ Server creation failed, using forced ID: {self.session_id}")
                return self.session_id
        except Exception as e:
            print(f"⚠️ Error creating session: {e}")
            # Use BANKAI anyway
            self.session_id = "BANKAI"
            print(f"🔧 Using forced session ID: {self.session_id}")
            return self.session_id
    
    def join_session(self, session_id: str) -> bool:
        """Join session - always return True for BANKAI"""
        if session_id == "BANKAI":
            print(f"✅ Force-joining session: {session_id}")
            self.session_id = session_id
            return True
        
        # For other session IDs, try normal join
        return super().join_session(session_id)
    
    def connect_as_host(self) -> bool:
        """Connect as host with forced BANKAI session"""
        try:
            print(f"🔗 Connecting to {self.server_url} as host...")
            
            # Force session ID to BANKAI
            self.session_id = "BANKAI"
            
            # Create WebSocket connection
            self.ws = websocket.WebSocket()
            self.ws.connect(self.server_url)
            self.connected = True
            
            print(f"🚀 WebSocket connected")
            
            # Send host connect message with BANKAI
            connect_msg = {
                "type": "connect",
                "role": "host",
                "sessionId": "BANKAI"
            }
            
            self.ws.send(json.dumps(connect_msg))
            self.role = 'host'
            
            # Start message handler
            def handle_messages():
                try:
                    while self.connected:
                        try:
                            message = self.ws.recv()
                            if message:
                                self._handle_message(json.loads(message))
                        except websocket.WebSocketTimeoutError:
                            continue
                        except Exception as e:
                            if self.connected:
                                print(f"Message handler error: {e}")
                            break
                except Exception as e:
                    print(f"Handler thread error: {e}")
                finally:
                    self.connected = False
            
            msg_thread = threading.Thread(target=handle_messages, daemon=True)
            msg_thread.start()
            
            # Wait for connection confirmation
            time.sleep(1)
            
            print(f"✅ Connected with session ID: {self.session_id}")
            
            if self.on_connection_change:
                self.on_connection_change("host_ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False


def main():
    try:
        print("🚀 Starting BANKAI host with FORCED session ID...")
        
        relay = BankaiRelayClient("wss://sync-hello.onrender.com")
        capture = OptimizedScreenCapture()
        input_handler = OptimizedInputHandler()
        
        # Callbacks
        def on_screen_data(data):
            pass  # Host doesn't expect screen data
            
        def on_input_data(data):
            print(f"Received input data: {data}")
            try:
                input_handler.handle_remote_input(data)
            except Exception as e:
                print(f"Input handler error: {e}")
                
        def on_conn(status):
            print(f"Connection status: {status}")
        
        relay.on_screen_data = on_screen_data
        relay.on_input_data = on_input_data
        relay.on_connection_change = on_conn
        
        # Force create BANKAI session
        created_session = relay.create_session("BANKAI")
        print(f"SESSION_ID:{created_session}")
        
        # Write session ID to file
        with open("bankai_session.txt", "w", encoding='utf-8') as f:
            f.write(f"{created_session}\n")
        
        # Connect as host with forced BANKAI
        if not relay.connect_as_host():
            print("❌ Failed to connect as host!")
            return
            
        print("✅ Connected as host successfully!")
        print("🖥️ Host ready - waiting for client...")
        
        # Start capture loop
        def capture_loop():
            try:
                while relay.is_connected() and relay.role == 'host':
                    screen = capture.capture_screen()
                    if screen and 'data' in screen:
                        try:
                            relay.send_screen_data(screen['data'])
                        except Exception as e:
                            print(f"Error sending screen: {e}")
                    time.sleep(1/30)  # 30 FPS
            except Exception as e:
                print(f"Capture loop error: {e}")
        
        t = threading.Thread(target=capture_loop, daemon=True)
        t.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        try:
            relay.disconnect()
            if os.path.exists("bankai_session.txt"):
                os.remove("bankai_session.txt")
        except:
            pass


if __name__ == "__main__":
    main()