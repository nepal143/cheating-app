#!/usr/bin/env python3
"""
Test script to verify image compression works correctly
"""

from screen_capture import ScreenCapture
import time

def test_screen_capture():
    """Test screen capture compression"""
    print("Testing screen capture compression...")
    
    capture = ScreenCapture()
    
    for i in range(5):
        print(f"\nCapture test {i+1}:")
        screen_data = capture.capture_screen()
        
        if screen_data:
            data_size = len(screen_data['data'])
            print(f"✓ Capture successful!")
            print(f"  - Image size: {data_size} bytes ({data_size/1024:.1f} KB)")
            print(f"  - Resolution: {screen_data['width']}x{screen_data['height']}")
            print(f"  - Timestamp: {screen_data['timestamp']}")
            
            # Verify it's valid JPEG data
            if screen_data['data'].startswith(b'\xff\xd8'):
                print("  - ✓ Valid JPEG header detected")
            else:
                print("  - ✗ Invalid JPEG header!")
                
        else:
            print("✗ Capture failed!")
            
        time.sleep(1)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_screen_capture()
