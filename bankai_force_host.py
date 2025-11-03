#!/usr/bin/env python3
"""
bankai_force_host.py - Force session ID to be "BANKAI"
This creates a host that tries to force the session ID to "BANKAI"
"""
import sys
import time
import threading
import os
import requests
import json

from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler


class BankaiRelayClient(RelayClient):
    """Modified relay client that forces session ID to BANKAI"""
    
    def create_session(self, forced_id: str = None) -> str:
        """Create a new session with forced ID"""
        try:
            # Try to create session with specific ID
            if forced_id:
                payload = {"sessionId": forced_id}
                response = requests.post(f"{self.http_url}/api/session/create", 
                                       json=payload, timeout=10)
            else:
                response = requests.post(f"{self.http_url}/api/session/create", timeout=10)
                
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('sessionId', forced_id)
                print(f"✅ Session created: {self.session_id}")
                return self.session_id
            else:
                # Fallback: try to join existing session
                if forced_id:
                    print(f"Creating with forced ID failed, trying to join existing {forced_id}...")
                    if self.join_session(forced_id):
                        self.session_id = forced_id
                        print(f"✅ Joined existing session: {self.session_id}")
                        return self.session_id
                
                raise Exception(f"Failed to create session: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            # Last resort: just use the forced ID anyway
            if forced_id:
                print(f"Using forced ID anyway: {forced_id}")
                self.session_id = forced_id
                return forced_id
            return None


def main():
    try:
        session_id = "BANKAI"
        
        print(f"Starting BANKAI host with forced session ID: {session_id}")
        
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
        
        # Create session with forced ID
        created_session = relay.create_session(session_id)
        if not created_session:
            print("Failed to create session!")
            return
            
        print(f"SESSION_ID:{created_session}")
        
        # Write session ID to file
        with open("bankai_session.txt", "w", encoding='utf-8') as f:
            f.write(f"{created_session}\n")
        
        # Connect as host
        if not relay.connect_as_host():
            print("Failed to connect as host!")
            return
            
        print("Connected as host successfully!")
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
        print("\nShutting down...")
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