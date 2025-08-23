#!/usr/bin/env python3
"""
Test script for advanced stealth features
"""

import time
import psutil
import subprocess

def test_process_detection():
    """Test if we can detect security software"""
    print("Testing process detection...")
    
    security_processes = [
        'respondus', 'lockdown', 'browser', 'seb', 'safebrowser',
        'examplify', 'proctoru', 'examity', 'respondusmonitor'
    ]
    
    found_security = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            for security in security_processes:
                if security in proc_name:
                    print(f"⚠️  Security software detected: {proc.info['name']}")
                    found_security = True
        except:
            continue
    
    if not found_security:
        print("✅ No security software detected")
    
    return found_security

def test_decoy_creation():
    """Test creating decoy processes"""
    print("\nTesting decoy process creation...")
    
    try:
        # Create a simple decoy process
        proc = subprocess.Popen(
            'ping localhost -n 5', 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"✅ Created decoy process with PID: {proc.pid}")
        
        # Let it run for a moment
        time.sleep(2)
        
        # Clean it up
        proc.terminate()
        print("✅ Decoy process cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Decoy creation failed: {e}")
        return False

def test_vm_detection():
    """Test VM detection capabilities"""
    print("\nTesting VM detection...")
    
    vm_indicators = ['VMware', 'VirtualBox', 'VBOX', 'QEMU', 'Xen']
    
    try:
        # Check system manufacturer
        result = subprocess.check_output('wmic computersystem get manufacturer', shell=True, text=True)
        
        vm_detected = False
        for indicator in vm_indicators:
            if indicator.lower() in result.lower():
                print(f"⚠️  VM detected: {indicator}")
                vm_detected = True
                
        if not vm_detected:
            print("✅ No VM environment detected")
            
        return vm_detected
        
    except Exception as e:
        print(f"❌ VM detection failed: {e}")
        return False

def main():
    print("🔍 Testing Advanced Stealth Features")
    print("=" * 40)
    
    # Test security software detection
    security_detected = test_process_detection()
    
    # Test decoy process creation
    decoy_success = test_decoy_creation()
    
    # Test VM detection
    vm_detected = test_vm_detection()
    
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print(f"Security Software: {'Detected' if security_detected else 'Not Detected'}")
    print(f"Decoy Processes: {'Working' if decoy_success else 'Failed'}")
    print(f"VM Environment: {'Detected' if vm_detected else 'Not Detected'}")
    
    if security_detected:
        print("\n⚠️  Security software detected - advanced bypass recommended")
    else:
        print("\n✅ Environment appears safe for stealth operations")

if __name__ == "__main__":
    main()
