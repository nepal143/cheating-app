"""
Networking Module
Handles secure server and client connections.
"""

import socket
import threading
import json
import time
import struct
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

class SecureServer:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.is_running = False
        self.is_client_connected = False
        self.lock = threading.Lock()
        
    def start(self, port=9999):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(1.0)  # Non-blocking accept
            
            self.is_running = True
            
            # Start connection handler thread
            connection_thread = threading.Thread(target=self._handle_connections, daemon=True)
            connection_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Server start error: {e}")
            return False
            
    def stop(self):
        """Stop the server"""
        self.is_running = False
        
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
                self.is_client_connected = False
                
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
                self.server_socket = None
                
    def _handle_connections(self):
        """Handle incoming client connections"""
        while self.is_running:
            try:
                if not self.is_client_connected:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Perform handshake
                    if self._perform_handshake(client_socket):
                        with self.lock:
                            self.client_socket = client_socket
                            self.client_address = client_address
                            self.is_client_connected = True
                        print(f"Client connected from {client_address}")
                    else:
                        client_socket.close()
                        
                time.sleep(0.1)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Connection handling error: {e}")
                    
    def _perform_handshake(self, client_socket):
        """Perform security handshake with client"""
        try:
            # Send server hello
            hello_data = {
                'type': 'server_hello',
                'version': '1.0',
                'encryption': 'fernet'
            }
            self._send_raw_data(client_socket, json.dumps(hello_data).encode())
            
            # Receive client hello
            response = self._receive_raw_data(client_socket)
            if not response:
                return False
                
            client_hello = json.loads(response.decode())
            if client_hello.get('type') != 'client_hello':
                return False
                
            # Exchange encryption keys (simplified for demo)
            encryption_key = Fernet.generate_key()
            key_data = {
                'type': 'encryption_key',
                'key': base64.b64encode(encryption_key).decode()
            }
            self._send_raw_data(client_socket, json.dumps(key_data).encode())
            
            # Set up encryption
            self.crypto_manager.set_key(encryption_key)
            
            return True
            
        except Exception as e:
            print(f"Handshake error: {e}")
            return False
            
    def has_client(self):
        """Check if a client is connected"""
        return self.is_client_connected
        
    def is_connected(self):
        """Check if server is connected to a client"""
        return self.is_client_connected
        
    def send_screen_data(self, screen_data):
        """Send screen data to connected client"""
        try:
            with self.lock:
                if not self.client_socket or not self.is_client_connected:
                    return False
                    
                # Compress screen data with balanced compression
                compressed_data = zlib.compress(screen_data['data'], level=6)  # Balanced compression
                
                # Create packet
                packet = {
                    'type': 'screen_data',
                    'width': screen_data['width'],
                    'height': screen_data['height'],
                    'compressed': True,
                    'data': base64.b64encode(compressed_data).decode(),
                    'timestamp': screen_data['timestamp']
                }
                
                # Encrypt and send
                encrypted_data = self.crypto_manager.encrypt(json.dumps(packet))
                return self._send_encrypted_data(self.client_socket, encrypted_data)
                
        except Exception as e:
            print(f"Send screen data error: {e}")
            # Don't disconnect immediately, just log the error
            return False
            
    def receive_input(self):
        """Receive input data from client"""
        try:
            with self.lock:
                if not self.client_socket or not self.is_client_connected:
                    return None
                    
                # Set very short timeout for input - check frequently
                self.client_socket.settimeout(0.001)
                encrypted_data = self._receive_encrypted_data(self.client_socket)
                
                if encrypted_data:
                    decrypted_data = self.crypto_manager.decrypt(encrypted_data)
                    input_data = json.loads(decrypted_data)
                    return input_data
                    
                return None
                
        except socket.timeout:
            return None
        except Exception as e:
            # Don't disconnect on input receive errors
            return None
            
    def _disconnect_client(self):
        """Disconnect the current client"""
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
                self.client_address = None
                self.is_client_connected = False
                
    def _send_raw_data(self, sock, data):
        """Send raw data with length prefix"""
        try:
            # Send length first
            length = len(data)
            sock.sendall(struct.pack('!I', length))
            # Send data
            sock.sendall(data)
            return True
        except:
            return False
            
    def _receive_raw_data(self, sock):
        """Receive raw data with length prefix"""
        try:
            # Receive length first
            length_data = self._receive_exact(sock, 4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            # Sanity check on length to prevent memory issues
            if length > 5000000:  # 5MB max for good quality images
                print(f"Data too large: {length} bytes")
                return None
                
            # Receive data
            return self._receive_exact(sock, length)
        except struct.error as e:
            print(f"Struct unpack error: {e}")
            return None
        except Exception as e:
            print(f"Receive raw data error: {e}")
            return None
            
    def _send_encrypted_data(self, sock, data):
        """Send encrypted data"""
        return self._send_raw_data(sock, data)
        
    def _receive_encrypted_data(self, sock):
        """Receive encrypted data"""
        return self._receive_raw_data(sock)
        
    def _receive_exact(self, sock, length):
        """Receive exact amount of data"""
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data


class SecureClient:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
        self.client_socket = None
        self.is_connected_flag = False
        self.lock = threading.Lock()
        
    def connect(self, server_ip, server_port):
        """Connect to the server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)  # 10 second timeout
            self.client_socket.connect((server_ip, server_port))
            
            # Perform handshake
            if self._perform_handshake():
                self.is_connected_flag = True
                return True
            else:
                self.client_socket.close()
                return False
                
        except Exception as e:
            print(f"Client connect error: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from server"""
        self.is_connected_flag = False
        
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
                
    def _perform_handshake(self):
        """Perform security handshake with server"""
        try:
            # Receive server hello
            response = self._receive_raw_data(self.client_socket)
            if not response:
                return False
                
            server_hello = json.loads(response.decode())
            if server_hello.get('type') != 'server_hello':
                return False
                
            # Send client hello
            hello_data = {
                'type': 'client_hello',
                'version': '1.0',
                'capabilities': ['screen_view', 'remote_input']
            }
            self._send_raw_data(self.client_socket, json.dumps(hello_data).encode())
            
            # Receive encryption key
            key_response = self._receive_raw_data(self.client_socket)
            if not key_response:
                return False
                
            key_data = json.loads(key_response.decode())
            if key_data.get('type') != 'encryption_key':
                return False
                
            # Set up encryption
            encryption_key = base64.b64decode(key_data['key'].encode())
            self.crypto_manager.set_key(encryption_key)
            
            return True
            
        except Exception as e:
            print(f"Client handshake error: {e}")
            return False
            
    def is_connected(self):
        """Check if client is connected"""
        return self.is_connected_flag
        
    def receive_screen_data(self):
        """Receive screen data from server"""
        try:
            with self.lock:
                if not self.client_socket or not self.is_connected_flag:
                    return None
                    
                # Set a longer timeout for screen data
                self.client_socket.settimeout(5.0)
                encrypted_data = self._receive_encrypted_data(self.client_socket)
                
                if encrypted_data:
                    decrypted_data = self.crypto_manager.decrypt(encrypted_data)
                    packet = json.loads(decrypted_data)
                    
                    if packet.get('type') == 'screen_data':
                        # Decompress if needed
                        if packet.get('compressed'):
                            compressed_data = base64.b64decode(packet['data'].encode())
                            screen_data = zlib.decompress(compressed_data)
                        else:
                            screen_data = base64.b64decode(packet['data'].encode())
                            
                        return {
                            'width': packet['width'],
                            'height': packet['height'],
                            'data': screen_data,
                            'timestamp': packet['timestamp']
                        }
                        
                return None
                
        except socket.timeout:
            # Timeout is normal, just return None
            return None
        except Exception as e:
            print(f"Receive screen data error: {e}")
            # Don't crash on errors, just skip this frame
            return None
            
    def send_input(self, input_data):
        """Send input data to server with high priority"""
        try:
            with self.lock:
                if not self.client_socket or not self.is_connected_flag:
                    return False
                    
                # Input has higher priority - use shorter timeout
                self.client_socket.settimeout(0.5)
                
                # Encrypt and send immediately
                encrypted_data = self.crypto_manager.encrypt(json.dumps(input_data))
                return self._send_encrypted_data(self.client_socket, encrypted_data)
                
        except Exception as e:
            # Don't print errors for input to avoid spam
            return False
            
    def _send_raw_data(self, sock, data):
        """Send raw data with length prefix"""
        try:
            length = len(data)
            sock.sendall(struct.pack('!I', length))
            sock.sendall(data)
            return True
        except:
            return False
            
    def _receive_raw_data(self, sock):
        """Receive raw data with length prefix"""
        try:
            length_data = self._receive_exact(sock, 4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            # Sanity check on length to prevent memory issues
            if length > 5000000:  # 5MB max for good quality images
                print(f"Data too large: {length} bytes")
                return None
                
            return self._receive_exact(sock, length)
        except struct.error as e:
            print(f"Client struct unpack error: {e}")
            return None
        except Exception as e:
            print(f"Client receive raw data error: {e}")
            return None
            
    def _send_encrypted_data(self, sock, data):
        """Send encrypted data"""
        return self._send_raw_data(sock, data)
        
    def _receive_encrypted_data(self, sock):
        """Receive encrypted data"""
        return self._receive_raw_data(sock)
        
    def _receive_exact(self, sock, length):
        """Receive exact amount of data"""
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
