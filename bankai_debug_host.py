#!/usr/bin/env python3
"""
bankai_debug_host.py - Debug version to see what's happening
"""
import sys
import time
import threading
import os

from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler


def main():
    try:
        print("Starting bankai host...")
        
        relay = RelayClient("wss://sync-hello.onrender.com")
        capture = OptimizedScreenCapture()
        input_handler = OptimizedInputHandler()
        
        print("Initialized relay and capture...")
        
        # Callbacks (with debug)
        def on_screen_data(data):
            print("Received screen data (unexpected on host)")
            
        def on_input_data(data):
            print(f"Received input data: {data}")
            try:
                input_handler.handle_remote_input(data)
            except Exception as e:
                print(f"Input handler error: {e}")
                
        def on_conn(status):
            print(f"Connection status: {status}")
        
        relay.on_screen_data = on_screen_data
        relay.on_input_data = on_input_data
        relay.on_connection_change = on_conn
        
        print("Setting up callbacks...")
        
        # Create session
        print("Creating session...")
        created_session = relay.create_session()
        if not created_session:
            print("Failed to create session!")
            return
            
        print(f"Session created: {created_session}")
        
        # Write session ID to file for clients to find
        with open("bankai_session.txt", "w", encoding='utf-8') as f:
            f.write(f"{created_session}\n")
        print("Session ID written to file")
        
        # Connect as host
        print("Connecting as host...")
        if not relay.connect_as_host():
            print("Failed to connect as host!")
            return
            
        print("Connected as host successfully!")
        
        # Start capture loop in background thread
        def capture_loop():
            try:
                print("Starting capture loop...")
                while relay.is_connected() and relay.role == 'host':
                    screen = capture.capture_screen()
                    if screen and 'data' in screen:
                        try:
                            relay.send_screen_data(screen['data'])
                            print(".", end="", flush=True)  # Progress indicator
                        except Exception as e:
                            print(f"Error sending screen: {e}")
                    time.sleep(1/10)  # 10 FPS for testing
            except Exception as e:
                print(f"Capture loop error: {e}")
        
        t = threading.Thread(target=capture_loop, daemon=True)
        t.start()
        
        print("Capture thread started. Host is ready!")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        try:
            relay.disconnect()
            if os.path.exists("bankai_session.txt"):
                os.remove("bankai_session.txt")
        except:
            pass


if __name__ == "__main__":
    main()