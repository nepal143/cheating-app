#!/usr/bin/env python3
"""
modified_relay_client.py - Modified relay client that forces BANKAI as session ID
"""

import websocket
import json
import threading
import time
import requests
import base64
from typing import Optional, Callable

class RelayClient:
    def __init__(self, server_url: str = "wss://sync-hello.onrender.com"):
        self.server_url = server_url
        self.http_url = server_url.replace('wss://', 'https://').replace('ws://', 'http://')
        self.ws: Optional[websocket.WebSocket] = None
        self.session_id: Optional[str] = None
        self.connected = False
        self.role: Optional[str] = None  # 'host' or 'client'
        
        # Callbacks
        self.on_screen_data: Optional[Callable] = None
        self.on_input_data: Optional[Callable] = None
        self.on_connection_change: Optional[Callable] = None
        
    def create_session(self) -> str:
        """Create a new session and FORCE return 'BANKAI'"""
        try:
            # Try to create session normally first
            response = requests.post(f"{self.http_url}/api/session/create", timeout=10)
            if response.status_code == 200:
                data = response.json()
                server_session_id = data['sessionId']
                print(f"Server created: {server_session_id}, but forcing to BANKAI")
            else:
                print(f"Session creation failed with status {response.status_code}, using BANKAI anyway")
        except Exception as e:
            print(f"Session creation error: {e}, using BANKAI anyway")
        
        # ALWAYS force the session ID to be BANKAI
        self.session_id = "BANKAI"
        print(f"✅ Session forced to: {self.session_id}")
        return self.session_id
            
    def join_session(self, session_id: str) -> bool:
        """Check if session exists - always return True for BANKAI"""
        try:
            if session_id == "BANKAI":
                print(f"✅ Force-accepting BANKAI session")
                self.session_id = session_id
                return True
                
            # For other sessions, try normal join
            payload = {"sessionId": session_id}
            response = requests.post(f"{self.http_url}/api/session/join", 
                                   json=payload, timeout=10)
            if response.status_code == 200:
                self.session_id = session_id
                print(f"✅ Session joined: {self.session_id}")
                return True
            else:
                print(f"❌ Session not found: {session_id}")
                return False
        except Exception as e:
            print(f"❌ Error joining session: {e}")
            return False
    
    def connect_as_host(self) -> bool:
        """Connect to relay server as host"""
        try:
            print(f"🔗 Connecting to {self.server_url} as host...")
            
            # Force session to BANKAI if not already set
            if not self.session_id:
                self.session_id = "BANKAI"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    self._handle_message(data)
                except Exception as e:
                    print(f"Message handling error: {e}")
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
                self.connected = False
            
            def on_close(ws, close_status_code, close_msg):
                print("📴 WebSocket disconnected")
                self.connected = False
                if self.on_connection_change:
                    self.on_connection_change("disconnected")
            
            def on_open(ws):
                print("🚀 WebSocket connected")
                self.connected = True
                
                # Send connect message with BANKAI session
                connect_msg = {
                    "type": "connect",
                    "role": "host", 
                    "sessionId": "BANKAI"  # Force BANKAI
                }
                ws.send(json.dumps(connect_msg))
                self.role = 'host'
                
                # Generate unique client ID
                import uuid
                client_id = str(uuid.uuid4())
                print(f"✅ Connected with client ID: {client_id}")
                
                if self.on_connection_change:
                    self.on_connection_change("host_ready")
            
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_message=on_message,
                on_error=on_error, 
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket in separate thread
            def run_ws():
                self.ws.run_forever()
                
            ws_thread = threading.Thread(target=run_ws, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            timeout = 10
            while timeout > 0 and not self.connected:
                time.sleep(0.1)
                timeout -= 0.1
                
            return self.connected
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def connect_as_client(self, session_id: str = "BANKAI") -> bool:
        """Connect to relay server as client"""
        try:
            print(f"🔗 Connecting to {self.server_url} as client for session {session_id}...")
            
            self.session_id = session_id
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    self._handle_message(data)
                except Exception as e:
                    print(f"Message handling error: {e}")
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
                self.connected = False
            
            def on_close(ws, close_status_code, close_msg):
                print("📴 WebSocket disconnected")
                self.connected = False
                if self.on_connection_change:
                    self.on_connection_change("disconnected")
            
            def on_open(ws):
                print("🚀 WebSocket connected")
                self.connected = True
                
                # Send connect message
                connect_msg = {
                    "type": "connect",
                    "role": "client",
                    "sessionId": session_id
                }
                ws.send(json.dumps(connect_msg))
                self.role = 'client'
                
                if self.on_connection_change:
                    self.on_connection_change("client_ready")
            
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket in separate thread
            def run_ws():
                self.ws.run_forever()
                
            ws_thread = threading.Thread(target=run_ws, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            timeout = 10
            while timeout > 0 and not self.connected:
                time.sleep(0.1)
                timeout -= 0.1
                
            return self.connected
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def _handle_message(self, data):
        """Handle incoming WebSocket messages"""
        try:
            msg_type = data.get('type')
            
            if msg_type == 'screen_data':
                screen_data = data.get('data')
                if screen_data and self.on_screen_data:
                    self.on_screen_data(screen_data)
                    
            elif msg_type == 'input_data': 
                input_data = data.get('data')
                if input_data and self.on_input_data:
                    self.on_input_data(input_data)
                    
            elif msg_type == 'connection':
                status = data.get('status')
                if status and self.on_connection_change:
                    self.on_connection_change(status)
                    
        except Exception as e:
            print(f"Message handling error: {e}")
    
    def send_screen_data(self, screen_data):
        """Send screen data to relay server"""
        if self.connected and self.ws and self.role == 'host':
            try:
                # Encode as base64 if it's bytes
                if isinstance(screen_data, bytes):
                    screen_data = base64.b64encode(screen_data).decode('utf-8')
                
                message = {
                    "type": "screen_data",
                    "sessionId": self.session_id,
                    "data": screen_data
                }
                self.ws.send(json.dumps(message))
            except Exception as e:
                print(f"Error sending screen data: {e}")
    
    def send_input_data(self, input_data):
        """Send input data to relay server"""
        if self.connected and self.ws and self.role == 'client':
            try:
                message = {
                    "type": "input_data", 
                    "sessionId": self.session_id,
                    "data": input_data
                }
                self.ws.send(json.dumps(message))
            except Exception as e:
                print(f"Error sending input data: {e}")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.connected and self.ws is not None
    
    def disconnect(self):
        """Disconnect from relay server"""
        self.connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.role = None
        self.session_id = None


# Test the modified relay client
if __name__ == "__main__":
    print("Testing modified RelayClient with forced BANKAI session...")
    
    relay = RelayClient()
    
    def on_screen(data):
        print(f"📺 Received screen data: {len(data) if data else 0} bytes")
    
    def on_input(data):
        print(f"⌨️ Received input data: {data}")
    
    def on_conn(status):
        print(f"🔌 Connection status: {status}")
    
    relay.on_screen_data = on_screen
    relay.on_input_data = on_input
    relay.on_connection_change = on_conn
    
    # Test session creation
    session_id = relay.create_session()
    print(f"SESSION_ID:{session_id}")
    
    # Test host connection
    if relay.connect_as_host():
        print("🖥️ Host ready - waiting for client...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
    else:
        print("❌ Failed to connect as host")
    
    relay.disconnect()