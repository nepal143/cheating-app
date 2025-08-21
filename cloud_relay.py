#!/usr/bin/env python3
"""
Cloud Relay - Simple cloud-based relay for remote desktop connections
Works behind any firewall/NAT without port forwarding
"""
import socket
import threading
import requests
import json
import time
import base64
import os
from datetime import datetime
import uuid

class CloudRelay:
    """Cloud-based relay service"""
    
    def __init__(self):
        # Using free services for relay
        self.relay_services = [
            {
                'name': 'JSONBin',
                'base_url': 'https://api.jsonbin.io/v3/b',
                'headers': {'Content-Type': 'application/json'}
            },
            {
                'name': 'RequestBin', 
                'base_url': 'https://httpbin.org/post',
                'headers': {'Content-Type': 'application/json'}
            }
        ]
        self.session_id = None
        self.relay_data = {}
        
    def create_relay_session(self):
        """Create a relay session in the cloud"""
        session_id = f"rd-{uuid.uuid4().hex[:8]}"
        
        session_data = {
            'session_id': session_id,
            'created_time': datetime.now().isoformat(),
            'server_info': None,
            'client_info': None,
            'messages': [],
            'status': 'waiting'
        }
        
        # Try JSONBin first
        try:
            response = requests.post(
                self.relay_services[0]['base_url'],
                json=session_data,
                headers=self.relay_services[0]['headers'],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'metadata' in result:
                    self.session_id = result['metadata']['id']
                    return {
                        'success': True,
                        'session_id': self.session_id,
                        'relay_url': f"Relay-{self.session_id}"
                    }
        except Exception as e:
            print(f"JSONBin failed: {e}")
        
        # Fallback: Use local file-based relay
        import os
        relay_dir = os.path.join(os.path.dirname(__file__), 'relay_sessions')
        os.makedirs(relay_dir, exist_ok=True)
        
        session_file = os.path.join(relay_dir, f"{session_id}.json")
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            
            self.session_id = session_id
            return {
                'success': True,
                'session_id': session_id,
                'relay_url': f"Local-{session_id}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def register_server(self, session_id, server_info):
        """Register server in relay session"""
        try:
            # Try to update cloud session
            if session_id.startswith('Local-'):
                # Local file relay
                session_file = os.path.join(os.path.dirname(__file__), 'relay_sessions', f"{session_id[6:]}.json")
                
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                data['server_info'] = server_info
                data['status'] = 'server_ready'
                
                with open(session_file, 'w') as f:
                    json.dump(data, f)
                
                return True
            else:
                # Cloud relay
                response = requests.get(f"https://api.jsonbin.io/v3/b/{session_id}")
                data = response.json()['record']
                
                data['server_info'] = server_info
                data['status'] = 'server_ready'
                
                requests.put(
                    f"https://api.jsonbin.io/v3/b/{session_id}",
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
                return True
                
        except Exception as e:
            print(f"Register server error: {e}")
            return False
    
    def get_session_info(self, session_id):
        """Get session information"""
        try:
            if session_id.startswith('Local-'):
                # Local file relay
                session_file = os.path.join(os.path.dirname(__file__), 'relay_sessions', f"{session_id[6:]}.json")
                
                with open(session_file, 'r') as f:
                    return json.load(f)
            else:
                # Cloud relay
                response = requests.get(f"https://api.jsonbin.io/v3/b/{session_id}")
                return response.json()['record']
                
        except Exception as e:
            print(f"Get session error: {e}")
            return None

class DirectConnect:
    """Simple direct connection without complex networking"""
    
    def __init__(self):
        self.local_servers = []
        
    def find_local_servers(self):
        """Scan local network for running servers"""
        import threading
        
        def scan_ip(ip):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, 9999))
                sock.close()
                
                if result == 0:
                    self.local_servers.append(ip)
            except:
                pass
        
        # Get local network range
        local_ip = self.get_local_ip()
        network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
        
        threads = []
        for i in range(1, 255):
            ip = network_base + str(i)
            thread = threading.Thread(target=scan_ip, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all scans
        for thread in threads:
            thread.join()
        
        return self.local_servers
    
    def get_local_ip(self):
        """Get local IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

# Test the cloud relay
if __name__ == "__main__":
    print("☁️ Testing Cloud Relay Service...")
    
    relay = CloudRelay()
    
    print("🔄 Creating relay session...")
    result = relay.create_relay_session()
    
    if result['success']:
        print(f"✅ Relay session created!")
        print(f"🆔 Session ID: {result['session_id']}")
        print(f"🔗 Relay URL: {result['relay_url']}")
        print()
        print("💡 How to use:")
        print("1. Server: Register with this session ID")
        print("2. Client: Connect using this session ID")
        print("3. All traffic goes through cloud relay")
        print("4. No port forwarding needed!")
        
        # Test registering server
        print("\n🔄 Testing server registration...")
        server_info = {
            'local_ip': relay.CloudRelay().get_local_ip() if hasattr(CloudRelay, 'get_local_ip') else '127.0.0.1',
            'ready_time': datetime.now().isoformat()
        }
        
        if relay.register_server(result['session_id'], server_info):
            print("✅ Server registered successfully!")
        else:
            print("❌ Server registration failed")
            
    else:
        print(f"❌ Relay failed: {result.get('error', 'Unknown error')}")
        
    print("\n🔍 Testing local network scan...")
    direct = DirectConnect()
    servers = direct.find_local_servers()
    
    if servers:
        print(f"✅ Found {len(servers)} local servers: {servers}")
    else:
        print("❌ No local servers found on port 9999")
