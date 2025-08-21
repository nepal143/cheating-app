#!/usr/bin/env python3
"""
P2P Connection Helper - Connect directly without port forwarding
Uses STUN servers to establish direct peer-to-peer connections
"""
import socket
import threading
import json
import time
import random
import struct

class STUNClient:
    """Simple STUN client to get external IP and port"""
    
    STUN_SERVERS = [
        ("stun.l.google.com", 19302),
        ("stun1.l.google.com", 19302),
        ("stun2.l.google.com", 19302),
        ("stun.stunprotocol.org", 3478),
    ]
    
    def get_external_ip_port(self, local_port=9999):
        """Get external IP and port using STUN"""
        for stun_host, stun_port in self.STUN_SERVERS:
            try:
                # Create UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('', local_port))
                
                # STUN Binding Request
                trans_id = random.getrandbits(96).to_bytes(12, 'big')
                stun_request = struct.pack('!HHI', 0x0001, 0, 0x2112A442) + trans_id
                
                # Send STUN request
                sock.sendto(stun_request, (stun_host, stun_port))
                sock.settimeout(5)
                
                # Receive response
                data, addr = sock.recvfrom(1024)
                
                # Parse STUN response
                if len(data) >= 20:
                    # Look for MAPPED-ADDRESS attribute (0x0001)
                    offset = 20
                    while offset < len(data):
                        attr_type = struct.unpack('!H', data[offset:offset+2])[0]
                        attr_len = struct.unpack('!H', data[offset+2:offset+4])[0]
                        
                        if attr_type == 0x0001:  # MAPPED-ADDRESS
                            family = struct.unpack('!H', data[offset+5:offset+7])[0]
                            if family == 0x01:  # IPv4
                                port = struct.unpack('!H', data[offset+6:offset+8])[0]
                                ip_bytes = data[offset+8:offset+12]
                                ip = socket.inet_ntoa(ip_bytes)
                                
                                sock.close()
                                return {'ip': ip, 'port': port, 'success': True}
                        
                        offset += 4 + attr_len
                
                sock.close()
                
            except Exception as e:
                continue
        
        return {'success': False, 'error': 'All STUN servers failed'}

class P2PConnector:
    """Establish P2P connections without port forwarding"""
    
    def __init__(self):
        self.stun_client = STUNClient()
        
    def create_p2p_session(self):
        """Create a P2P session that others can join"""
        # Get external IP and port
        result = self.stun_client.get_external_ip_port()
        
        if not result['success']:
            return {'success': False, 'error': 'Cannot determine external IP'}
        
        external_ip = result['ip']
        external_port = result['port']
        
        # Create session info
        session_info = {
            'external_ip': external_ip,
            'external_port': external_port,
            'session_id': f"p2p-{random.randint(10000, 99999)}",
            'created_time': time.time()
        }
        
        return {
            'success': True,
            'session_info': session_info,
            'connection_string': f"{external_ip}:{external_port}"
        }
    
    def test_p2p_connectivity(self, target_ip, target_port):
        """Test if P2P connection is possible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Send UDP packet to target
            test_message = b"P2P_TEST"
            sock.sendto(test_message, (target_ip, target_port))
            
            # Try to receive response
            try:
                data, addr = sock.recvfrom(1024)
                sock.close()
                return {'success': True, 'responsive': True}
            except socket.timeout:
                sock.close()
                return {'success': True, 'responsive': False, 'note': 'Sent packet but no response'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Simple WebRTC-like signaling for P2P
class P2PSignaling:
    """Simple signaling server for P2P connections"""
    
    def __init__(self):
        self.sessions = {}
        
    def create_offer(self, session_id, connection_info):
        """Create connection offer"""
        self.sessions[session_id] = {
            'offer': connection_info,
            'answer': None,
            'created': time.time()
        }
        return session_id
    
    def create_answer(self, session_id, connection_info):
        """Respond to connection offer"""
        if session_id in self.sessions:
            self.sessions[session_id]['answer'] = connection_info
            return True
        return False
    
    def get_session(self, session_id):
        """Get session information"""
        return self.sessions.get(session_id)

# Test P2P connectivity
if __name__ == "__main__":
    print("🔗 Testing P2P Connection Setup...")
    
    connector = P2PConnector()
    
    print("📡 Getting external IP using STUN...")
    session = connector.create_p2p_session()
    
    if session['success']:
        print(f"✅ P2P Session Created!")
        print(f"🌍 External IP: {session['session_info']['external_ip']}")
        print(f"🚪 External Port: {session['session_info']['external_port']}")
        print(f"🔗 Connection String: {session['connection_string']}")
        print(f"🆔 Session ID: {session['session_info']['session_id']}")
        print()
        print("💡 Share this connection string with the client!")
        print("⚠️ Note: P2P may still require router cooperation")
    else:
        print(f"❌ P2P Setup Failed: {session['error']}")
        print("💡 P2P not possible, use relay/tunnel method instead")
