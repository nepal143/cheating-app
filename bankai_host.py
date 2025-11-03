#!/usr/bin/env python3
"""
bankai_host.py - Headless host/server for IgniteRemote

This script creates a relay session, connects as host, and streams screen
captures using the existing `OptimizedScreenCapture` implementation.

Usage:
  py -3 bankai_host.py [--server wss://...] [--verbose]

It prints the session id it creates so remote clients can connect.
"""
import argparse
import logging
import sys
import time
import threading

from relay_client import RelayClient
from optimized_capture import OptimizedScreenCapture, OptimizedInputHandler


def main():
    parser = argparse.ArgumentParser(description="bankai headless host")
    parser.add_argument("--server", default=None, help="WebSocket server URL (wss://...)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="[bankai-host] %(levelname)s: %(message)s")

    server_url = args.server if args.server else "wss://sync-hello.onrender.com"

    relay = RelayClient(server_url)
    capture = OptimizedScreenCapture()
    input_handler = OptimizedInputHandler()

    # Callbacks
    def on_screen_data(data):
        # Host doesn't expect screen data from relay
        logging.debug("Received unexpected screen data on host")

    def on_input_data(data):
        logging.info(f"Received remote input: {data}")
        try:
            input_handler.handle_remote_input(data)
        except Exception as e:
            logging.error(f"Input handler error: {e}")

    def on_conn(status):
        logging.info(f"Connection status: {status}")

    relay.on_screen_data = on_screen_data
    relay.on_input_data = on_input_data
    relay.on_connection_change = on_conn

    # Create session
    session_id = relay.create_session()
    if not session_id:
        logging.error("Failed to create session. Exiting.")
        sys.exit(2)

    print(f"SESSION_ID:{session_id}")
    logging.info(f"Created session: {session_id}")

    # Connect as host
    if not relay.connect_as_host():
        logging.error("Failed to connect as host. Exiting.")
        sys.exit(3)

    logging.info("Connected as host. Starting capture loop.")

    # Start capture loop in background thread
    def capture_loop():
        try:
            while relay.is_connected() and relay.role == 'host':
                screen = capture.capture_screen()
                if screen and 'data' in screen:
                    try:
                        relay.send_screen_data(screen['data'])
                    except Exception as e:
                        logging.error(f"Error sending screen data: {e}")
                time.sleep(1/30)
        except Exception as e:
            logging.error(f"Capture loop error: {e}")

    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()

    try:
        # Keep main thread alive while background capture runs
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupted, shutting down host...")
        relay.disconnect()


if __name__ == "__main__":
    main()
