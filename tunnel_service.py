#!/usr/bin/env python3
"""
Tunnel Service - Create connections without port forwarding
Uses a relay server to connect two computers behind NAT/firewalls
"""
import socket
import threading
import json
import time
import requests
from datetime import datetime

class TunnelService:
    def __init__(self):
        self.relay_servers = [
            "serveo.net",
            "localhost.run", 
            "ngrok.io"  # Requires account but very reliable
        ]
        
    def create_serveo_tunnel(self, local_port=9999):
        """Create a tunnel using serveo.net (free, no signup)"""
        import subprocess
        import random
        
        # Generate a random subdomain
        subdomain = f"rd-{random.randint(1000, 9999)}"
        
        try:
            # Create SSH tunnel to serveo
            cmd = f'ssh -R {subdomain}:80:localhost:{local_port} serveo.net'
            process = subprocess.Popen(cmd, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            # Give it time to establish
            time.sleep(3)
            
            if process.poll() is None:  # Process is running
                tunnel_url = f"https://{subdomain}.serveo.net"
                return {
                    'success': True,
                    'tunnel_url': tunnel_url,
                    'local_port': local_port,
                    'process': process
                }
            else:
                return {'success': False, 'error': 'Failed to establish tunnel'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_localhost_run_tunnel(self, local_port=9999):
        """Create tunnel using localhost.run"""
        import subprocess
        
        try:
            cmd = f'ssh -R 80:localhost:{local_port} localhost.run'
            process = subprocess.Popen(cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            time.sleep(3)
            
            # Try to get the tunnel URL from output
            output = process.stdout.readline()
            if 'https://' in output:
                tunnel_url = output.strip()
                return {
                    'success': True,
                    'tunnel_url': tunnel_url,
                    'process': process
                }
            
            return {'success': False, 'error': 'Could not get tunnel URL'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class P2PRelay:
    """Simple P2P relay without port forwarding"""
    
    def __init__(self):
        # Use a simple relay service (you could host your own)
        self.relay_host = "jsonbin.io"  # Free JSON storage
        self.session_id = None
        
    def create_session(self):
        """Create a relay session"""
        try:
            session_data = {
                'type': 'remote_desktop_session',
                'created': datetime.now().isoformat(),
                'server_ready': False,
                'client_ready': False,
                'messages': []
            }
            
            # Create session on relay service
            response = requests.post(
                "https://api.jsonbin.io/v3/b",
                json=session_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.session_id = response.json()['metadata']['id']
                return self.session_id
            else:
                return None
                
        except Exception as e:
            print(f"Relay error: {e}")
            return None
    
    def join_session(self, session_id):
        """Join an existing relay session"""
        self.session_id = session_id
        return True
    
    def send_message(self, message):
        """Send message through relay"""
        if not self.session_id:
            return False
            
        try:
            # Get current session data
            response = requests.get(f"https://api.jsonbin.io/v3/b/{self.session_id}")
            session_data = response.json()['record']
            
            # Add new message
            session_data['messages'].append({
                'timestamp': datetime.now().isoformat(),
                'data': message
            })
            
            # Update session
            update_response = requests.put(
                f"https://api.jsonbin.io/v3/b/{self.session_id}",
                json=session_data,
                headers={"Content-Type": "application/json"}
            )
            
            return update_response.status_code == 200
            
        except Exception as e:
            print(f"Send error: {e}")
            return False

# Test the tunnel service
if __name__ == "__main__":
    print("🚀 Testing Tunnel Services...")
    
    tunnel = TunnelService()
    
    print("📡 Trying serveo.net tunnel...")
    result = tunnel.create_serveo_tunnel(9999)
    
    if result['success']:
        print(f"✅ Tunnel created: {result['tunnel_url']}")
        print("🎉 Share this URL instead of IP address!")
        print("⏳ Tunnel will stay active...")
        
        try:
            # Keep tunnel alive
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("🛑 Tunnel stopped")
            result['process'].terminate()
    else:
        print(f"❌ Tunnel failed: {result['error']}")
        print("💡 Try installing SSH client or use alternative method")
