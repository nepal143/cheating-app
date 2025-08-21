"""
Network Helper Utilities
Automatic IP discovery and network troubleshooting.
"""

import socket
import requests
import threading
import time

class NetworkHelper:
    @staticmethod
    def get_local_ip():
        """Get the local network IP address"""
        try:
            # Connect to a remote address to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def get_public_ip():
        """Get the public IP address"""
        try:
            response = requests.get("https://api.ipify.org?format=text", timeout=5)
            return response.text.strip()
        except Exception:
            return "Unable to detect"
    
    @staticmethod
    def test_port_open(host, port, timeout=5):
        """Test if a port is open and reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def get_network_info():
        """Get comprehensive network information"""
        local_ip = NetworkHelper.get_local_ip()
        public_ip = NetworkHelper.get_public_ip()
        
        return {
            'local_ip': local_ip,
            'public_ip': public_ip,
            'local_connection': f"{local_ip}:9999",
            'external_connection': f"{public_ip}:9999"
        }

class ImprovedSecureServer:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self.is_client_connected = False
        self.lock = threading.Lock()
        self.connection_count = 0
        
    def start(self, port=9999):
        """Start the server with better error handling"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Enable address reuse to avoid "Address already in use" errors
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set socket options for better performance
            self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # Bind to all interfaces
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)  # Allow up to 5 pending connections
            
            # Set timeout for accept() to make it interruptible
            self.server_socket.settimeout(1.0)
            
            self.is_running = True
            
            # Get network info
            network_info = NetworkHelper.get_network_info()
            print(f"Server started successfully!")
            print(f"Local network connection: {network_info['local_connection']}")
            print(f"External connection: {network_info['external_connection']}")
            print(f"Note: For external connections, ensure port {port} is forwarded in your router")
            
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True, network_info
            
        except socket.error as e:
            print(f"Server start error: {e}")
            if e.errno == 10048:  # Address already in use
                print("Port 9999 is already in use. Try closing other instances or use a different port.")
            return False, None
        except Exception as e:
            print(f"Unexpected server start error: {e}")
            return False, None
            
    def _accept_connections(self):
        """Accept client connections with timeout handling"""
        print("Waiting for client connections...")
        
        while self.is_running:
            try:
                client_sock, address = self.server_socket.accept()
                self.connection_count += 1
                print(f"Client connected from: {address} (Connection #{self.connection_count})")
                
                # Configure client socket
                client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                client_sock.settimeout(30.0)  # 30 second timeout for operations
                
                with self.lock:
                    # Disconnect any existing client
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except:
                            pass
                    
                    self.client_socket = client_sock
                    self.is_client_connected = True
                
                # Start screen streaming and input handling in separate threads
                threading.Thread(target=self._stream_screen, daemon=True).start()
                threading.Thread(target=self._handle_input, daemon=True).start()
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Accept connection error: {e}")
                    time.sleep(1)  # Brief pause before retrying
                
    def _stream_screen(self):
        """Stream screen data with connection monitoring"""
        from optimized_capture import OptimizedScreenCapture
        
        capture = OptimizedScreenCapture()
        consecutive_failures = 0
        
        print("Started screen streaming")
        
        while self.is_client_connected and self.client_socket:
            try:
                screen_data = capture.capture_screen()
                if screen_data:
                    success = self._send_screen_data(screen_data)
                    if success:
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        if consecutive_failures > 10:  # 10 consecutive send failures
                            print("Too many send failures, disconnecting client")
                            break
                
                time.sleep(0.016)  # ~60 FPS
                    
            except Exception as e:
                print(f"Screen streaming error: {e}")
                consecutive_failures += 1
                if consecutive_failures > 5:
                    break
                time.sleep(0.1)
        
        print("Screen streaming stopped")
        self.is_client_connected = False
                
    def _send_screen_data(self, screen_data):
        """Send screen data with better error handling"""
        try:
            if not self.client_socket:
                return False
                
            # Create header
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
            
            message = struct.pack('!II', header_length, data_length) + header_json + screen_data['data']
            
            return self._send_all(self.client_socket, message)
            
        except Exception as e:
            print(f"Send screen data error: {e}")
            return False
            
    def _send_all(self, sock, data):
        """Send all data with timeout handling"""
        try:
            sent = 0
            while sent < len(data):
                bytes_sent = sock.send(data[sent:])
                if bytes_sent == 0:
                    return False
                sent += bytes_sent
            return True
        except socket.timeout:
            print("Send timeout")
            return False
        except Exception as e:
            print(f"Send error: {e}")
            return False
            
    def _handle_input(self):
        """Handle input from client with timeout"""
        from optimized_capture import OptimizedInputHandler
        
        input_handler = OptimizedInputHandler()
        print("Started input handling")
        
        while self.is_client_connected and self.client_socket:
            try:
                data = self._receive_json_with_timeout(self.client_socket, 1.0)
                if data:
                    input_handler.handle_remote_input(data)
                    
            except Exception as e:
                print(f"Input handling error: {e}")
                break
        
        print("Input handling stopped")
                
    def _receive_json_with_timeout(self, sock, timeout):
        """Receive JSON data with timeout"""
        try:
            sock.settimeout(timeout)
            
            # Receive length
            length_data = self._receive_exact(sock, 4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            if length > 10000:  # 10KB max for input JSON
                return None
                
            # Receive data
            data = self._receive_exact(sock, length)
            if data:
                return json.loads(data.decode('utf-8'))
            return None
            
        except socket.timeout:
            return None  # Timeout is normal
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
            except socket.timeout:
                return None
            except Exception as e:
                print(f"Receive exact error: {e}")
                return None
        return data
        
    def stop(self):
        """Stop the server gracefully"""
        print("Stopping server...")
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
        print("Server stopped")

import json
import struct
