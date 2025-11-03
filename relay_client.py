#!/usr/bin/env python3
"""
Relay Client - Connects to our WebSocket relay server
This replaces the direct networking with server-mediated connections
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
        """Create a REAL session but display as BANKAI"""
        try:
            # Create a REAL session on the server
            response = requests.post(f"{self.http_url}/api/session/create", timeout=10)
            if response.status_code == 200:
                data = response.json()
                real_session = data['sessionId']
                self.session_id = real_session  # Use REAL session for connections
                print(f"✅ Session created: BANKAI (real: {real_session})")
                
                # Save mapping for user
                with open("bankai_mapping.txt", "w") as f:
                    f.write(f"DISPLAY: BANKAI\nREAL: {real_session}\nUSE IN CLIENT: {real_session}")
                
                return real_session  # Return REAL session
            else:
                print(f"❌ Session creation failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return None
            
    def join_session(self, session_id: str) -> bool:
        """Check if session exists"""
        try:
            payload = {"sessionId": session_id}
            response = requests.post(f"{self.http_url}/api/session/join", 
                                   json=payload, timeout=10)
            if response.status_code == 200:
                self.session_id = session_id
                print(f"✅ Session found: {session_id}")
                return True
            else:
                print(f"❌ Session not found: {session_id}")
                return False
        except Exception as e:
            print(f"❌ Error joining session: {e}")
            return False
            
    def connect_as_host(self) -> bool:
        """Connect as host (screen sharer)"""
        if not self.session_id:
            print("❌ No session ID. Create session first.")
            return False
            
        self.role = 'host'
        return self._connect_websocket()
        
    def connect_as_client(self, session_id: str) -> bool:
        """Connect as client (viewer)"""
        if not self.join_session(session_id):
            return False
            
        self.role = 'client'
        return self._connect_websocket()
        
    def _connect_websocket(self) -> bool:
        """Connect to WebSocket server"""
        try:
            print(f"🔗 Connecting to {self.server_url} as {self.role}...")
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            for _ in range(50):  # 5 seconds timeout
                if self.connected:
                    return True
                time.sleep(0.1)
                
            print("❌ Connection timeout")
            return False
            
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
            
    def _on_open(self, ws):
        """WebSocket opened"""
        print("🚀 WebSocket connected")
        
        # Join session with role using REAL session ID
        message = {
            "type": self.role,
            "sessionId": self.session_id  # Use the real session ID
        }
        ws.send(json.dumps(message))
        
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'connected':
                print(f"✅ Connected with client ID: {data.get('clientId')}")
                
            elif msg_type == 'host_ready':
                self.connected = True
                print("🖥️ Host ready - waiting for client...")
                if self.on_connection_change:
                    self.on_connection_change('host_ready')
                    
            elif msg_type == 'client_ready':
                self.connected = True
                print("👀 Client ready - waiting for host...")
                if self.on_connection_change:
                    self.on_connection_change('client_ready')
                    
            elif msg_type == 'client_connected':
                print("🎉 Client connected to your session!")
                if self.on_connection_change:
                    self.on_connection_change('client_connected')
                    
            elif msg_type == 'host_available':
                print("🎉 Host is available!")
                if self.on_connection_change:
                    self.on_connection_change('host_available')
                    
            elif msg_type == 'screen_data':
                # Relay screen data to callback
                if self.on_screen_data and 'data' in data:
                    self.on_screen_data(data['data'])
                    
            elif msg_type == 'input_data':
                # Relay input data to callback
                if self.on_input_data and 'data' in data:
                    self.on_input_data(data['data'])
                    
            elif msg_type == 'host_disconnected':
                print("📴 Host disconnected")
                if self.on_connection_change:
                    self.on_connection_change('host_disconnected')
                    
            elif msg_type == 'client_disconnected':
                print("📴 Client disconnected")
                if self.on_connection_change:
                    self.on_connection_change('client_disconnected')
                    
            elif msg_type == 'error':
                print(f"❌ Server error: {data.get('message')}")
                
            elif msg_type == 'pong':
                # Response to ping
                pass
                
        except Exception as e:
            print(f"❌ Error handling message: {e}")
            
    def _on_error(self, ws, error):
        """WebSocket error"""
        print(f"❌ WebSocket error: {error}")
        
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        print("📴 WebSocket disconnected")
        self.connected = False
        
    def send_screen_data(self, image_data: bytes):
        """Send screen data (host only)"""
        if not self.connected or self.role != 'host':
            return False
            
        try:
            # Convert to base64 for JSON transmission
            b64_data = base64.b64encode(image_data).decode('utf-8')
            
            message = {
                "type": "screen_data",
                "sessionId": self.session_id,
                "data": b64_data
            }
            
            self.ws.send(json.dumps(message))
            return True
            
        except Exception as e:
            print(f"❌ Error sending screen data: {e}")
            return False
            
    def send_input_data(self, input_data: dict):
        """Send input data (client only)"""
        if not self.connected or self.role != 'client':
            return False
            
        try:
            message = {
                "type": "input_data", 
                "sessionId": self.session_id,
                "data": input_data
            }
            
            self.ws.send(json.dumps(message))
            return True
            
        except Exception as e:
            print(f"❌ Error sending input data: {e}")
            return False
            
    def ping(self):
        """Send ping to keep connection alive"""
        if self.connected:
            try:
                self.ws.send(json.dumps({"type": "ping"}))
            except:
                pass
                
    def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            self.ws.close()
        self.connected = False
        self.session_id = None
        
    def is_connected(self) -> bool:
        """Check if connected and ready"""
        return self.connected

# Example usage
if __name__ == "__main__":
    # Test the relay client
    relay = RelayClient("wss://sync-hello.onrender.com")  # Your deployed server
    
    def on_screen_received(data):
        print(f"📺 Received screen data: {len(data)} bytes")
        
    def on_input_received(data):
        print(f"🖱️ Received input: {data}")
        
    def on_connection_change(status):
        print(f"🔄 Connection status: {status}")
    
    # Set callbacks
    relay.on_screen_data = on_screen_received
    relay.on_input_data = on_input_received
    relay.on_connection_change = on_connection_change
    
    # Test as host
    session_id = relay.create_session()
    if session_id:
        print(f"🎯 Share this session ID: {session_id}")
        
        if relay.connect_as_host():
            print("🖥️ Host connected successfully!")
            
            # Keep alive
            try:
                while True:
                    time.sleep(10)
                    relay.ping()
            except KeyboardInterrupt:
                print("\n👋 Disconnecting...")
                relay.disconnect()
