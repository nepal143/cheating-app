"""
Optimized Networking Module
Fixed binary data transmission without JSON corruption.
"""

import socket
import threading
import time
import struct
import json
from cryptography.fernet import Fernet

class OptimizedSecureServer:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
        self.server_socket = None
        self.client_socket = None
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
            self.is_running = True
            
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Server start error: {e}")
            return False
            
    def _accept_connections(self):
        """Accept client connections"""
        try:
            while self.is_running:
                client_sock, address = self.server_socket.accept()
                print(f"Client connected: {address}")
                
                with self.lock:
                    self.client_socket = client_sock
                    self.is_client_connected = True
                
                # Start screen streaming thread
                threading.Thread(target=self._stream_screen, daemon=True).start()
                # Start input handling thread  
                threading.Thread(target=self._handle_input, daemon=True).start()
                
        except Exception as e:
            if self.is_running:
                print(f"Accept connection error: {e}")
                
    def _stream_screen(self):
        """Stream screen data to client - OPTIMIZED"""
        from optimized_capture import OptimizedScreenCapture
        
        capture = OptimizedScreenCapture()
        
        while self.is_client_connected and self.client_socket:
            try:
                screen_data = capture.capture_screen()
                if screen_data:
                    self._send_screen_data(screen_data)
                time.sleep(0.01)  # ~100 FPS max
                    
            except Exception as e:
                print(f"Screen streaming error: {e}")
                break
                
    def _send_screen_data(self, screen_data):
        """Send screen data as pure binary - NO JSON CORRUPTION"""
        try:
            if not self.client_socket:
                return
                
            # Create header with metadata (JSON is fine for small metadata)
            header = {
                'type': 'screen',
                'width': screen_data['width'],
                'height': screen_data['height'],
                'data_size': len(screen_data['data']),
                'timestamp': screen_data['timestamp']
            }
            
            header_json = json.dumps(header).encode('utf-8')
            
            # Send header length + header + binary data
            header_length = len(header_json)
            data_length = len(screen_data['data'])
            
            # Pack: header_length(4) + data_length(4) + header + binary_data
            message = struct.pack('!II', header_length, data_length) + header_json + screen_data['data']
            
            if len(message) > 10000000:  # 10MB safety check
                print(f"Message too large: {len(message)} bytes, skipping")
                return
                
            self._send_all(self.client_socket, message)
            
        except Exception as e:
            print(f"Send screen data error: {e}")
            
    def _handle_input(self):
        """Handle input from client"""
        from optimized_capture import OptimizedInputHandler
        
        input_handler = OptimizedInputHandler()
        
        while self.is_client_connected and self.client_socket:
            try:
                data = self._receive_json(self.client_socket)
                if data:
                    input_handler.handle_remote_input(data)
            except Exception as e:
                print(f"Input handling error: {e}")
                break
                
    def _send_all(self, sock, data):
        """Send all data"""
        sent = 0
        while sent < len(data):
            try:
                bytes_sent = sock.send(data[sent:])
                if bytes_sent == 0:
                    raise ConnectionError("Socket closed")
                sent += bytes_sent
            except Exception as e:
                print(f"Send error: {e}")
                raise
                
    def _receive_json(self, sock):
        """Receive JSON data"""
        try:
            length_data = self._receive_exact(sock, 4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            if length > 10000:  # 10KB max for input JSON
                return None
                
            data = self._receive_exact(sock, length)
            if data:
                return json.loads(data.decode('utf-8'))
            return None
            
        except Exception as e:
            print(f"Receive JSON error: {e}")
            return None
            
    def _receive_exact(self, sock, length):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < length:
            try:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except Exception as e:
                print(f"Receive exact error: {e}")
                return None
        return data
        
    def stop(self):
        """Stop the server"""
        self.is_running = False
        self.is_client_connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

class OptimizedSecureClient:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
        self.socket = None
        self.is_connected = False
        self.receive_callback = None
        
    def connect(self, host, port=9999):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_connected = True
            
            # Start receiving thread
            threading.Thread(target=self._receive_data, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Connect error: {e}")
            return False
            
    def _receive_data(self):
        """Receive screen data - OPTIMIZED BINARY"""
        while self.is_connected and self.socket:
            try:
                # Receive header_length + data_length
                lengths = self._receive_exact(4 + 4)
                if not lengths:
                    continue
                    
                header_length, data_length = struct.unpack('!II', lengths)
                
                # Safety checks
                if header_length > 10000 or data_length > 10000000:  # 10KB header, 10MB data max
                    print(f"Invalid sizes: header={header_length}, data={data_length}")
                    continue
                    
                # Receive header
                header_data = self._receive_exact(header_length)
                if not header_data:
                    continue
                    
                # Receive binary data
                binary_data = self._receive_exact(data_length)
                if not binary_data:
                    continue
                    
                # Parse header
                header = json.loads(header_data.decode('utf-8'))
                
                # Reconstruct screen data
                screen_data = {
                    'type': header['type'],
                    'width': header['width'],
                    'height': header['height'],
                    'data': binary_data,  # Pure JPEG bytes
                    'timestamp': header['timestamp']
                }
                
                print(f"Received screen data: {len(binary_data)} bytes")
                
                # Send to callback
                if self.receive_callback:
                    self.receive_callback(screen_data)
                    
            except Exception as e:
                print(f"Receive data error: {e}")
                break
                
    def _receive_exact(self, length):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < length:
            try:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            except Exception as e:
                print(f"Receive exact error: {e}")
                return None
        return data
        
    def send_input(self, input_data):
        """Send input data to server"""
        try:
            if not self.socket:
                return
                
            data = json.dumps(input_data).encode('utf-8')
            length = len(data)
            
            message = struct.pack('!I', length) + data
            self._send_all(message)
            
        except Exception as e:
            print(f"Send input error: {e}")
            
    def _send_all(self, data):
        """Send all data"""
        sent = 0
        while sent < len(data):
            try:
                bytes_sent = self.socket.send(data[sent:])
                if bytes_sent == 0:
                    raise ConnectionError("Socket closed")
                sent += bytes_sent
            except Exception as e:
                print(f"Send error: {e}")
                raise
                
    def set_receive_callback(self, callback):
        """Set callback for received data"""
        self.receive_callback = callback
        
    def disconnect(self):
        """Disconnect from server"""
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
