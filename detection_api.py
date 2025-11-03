#!/usr/bin/env python3
"""
Real-time process detection API for browser testing
This creates a local web server that the browser can query for real process information
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import psutil
import threading
import time

class ProcessDetectionAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/processes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            processes = self.get_process_info()
            self.wfile.write(json.dumps(processes).encode())
            
        elif self.path == '/api/windows':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            windows = self.get_window_info()
            self.wfile.write(json.dumps(windows).encode())
            
        elif self.path == '/api/connections':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            connections = self.get_network_info()
            self.wfile.write(json.dumps(connections).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_process_info(self):
        """Get real process information"""
        processes = []
        ignite_found = False
        python_with_main = False
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                name = proc.info['name'] or ''
                exe = proc.info.get('exe', '') or ''
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Check for IgniteRemote specifically
                if 'ignite' in name.lower():
                    ignite_found = True
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'suspicious': True,
                        'reason': 'Contains "ignite" in process name'
                    })
                
                # Check for Python running main.py
                if 'python' in name.lower() and 'main.py' in cmdline_str.lower():
                    python_with_main = True
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'cmdline': cmdline_str,
                        'suspicious': True,
                        'reason': 'Python process running main.py'
                    })
                
                # Check for decoy processes (high PID system processes)
                system_names = ['svchost.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe']
                if name.lower() in [s.lower() for s in system_names] and proc.info['pid'] > 10000:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'suspicious': True,
                        'reason': 'System process with unusually high PID (possible decoy)'
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            'ignite_detected': ignite_found,
            'python_main_detected': python_with_main,
            'suspicious_processes': processes,
            'total_processes': len(list(psutil.process_iter()))
        }
    
    def get_window_info(self):
        """Get window information"""
        try:
            import win32gui
            
            windows = []
            
            def enum_windows_proc(hwnd, window_list):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        suspicious = any(keyword in window_text.lower() 
                                       for keyword in ['ignite', 'remote', 'desktop'])
                        window_list.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'suspicious': suspicious
                        })
                return True
            
            win32gui.EnumWindows(enum_windows_proc, windows)
            
            return {
                'windows': windows,
                'suspicious_count': len([w for w in windows if w['suspicious']])
            }
            
        except ImportError:
            return {
                'error': 'win32gui not available',
                'windows': [],
                'suspicious_count': 0
            }
    
    def get_network_info(self):
        """Get network connection information"""
        connections = []
        websocket_ports = [80, 443, 8080, 8443, 3000, 5000]
        websocket_count = 0
        
        try:
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    is_websocket = conn.raddr.port in websocket_ports
                    if is_websocket:
                        websocket_count += 1
                    
                    connections.append({
                        'local_port': conn.laddr.port if conn.laddr else None,
                        'remote_host': conn.raddr.ip if conn.raddr else None,
                        'remote_port': conn.raddr.port if conn.raddr else None,
                        'status': conn.status,
                        'suspicious': is_websocket and conn.raddr.port in [443, 80]
                    })
        except:
            pass
        
        return {
            'total_connections': len(connections),
            'websocket_connections': websocket_count,
            'connections': connections[:10]  # Limit to first 10 for privacy
        }

def start_detection_server():
    """Start the detection API server"""
    server = HTTPServer(('localhost', 8765), ProcessDetectionAPI)
    print("🔍 Process Detection API started on http://localhost:8765")
    print("   /api/processes - Get process information")
    print("   /api/windows - Get window information") 
    print("   /api/connections - Get network connections")
    server.serve_forever()

if __name__ == "__main__":
    start_detection_server()
