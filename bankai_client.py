#!/usr/bin/env python3
"""
bankai_client.py - Client-only viewer for IgniteRemote

This script runs only the client/viewer side: it connects to the relay server
as a client (viewer) for a given session code and opens a Tkinter window that
displays incoming frames using `OptimizedRemoteViewer` from `optimized_capture.py`.

It does NOT start any screen capture or host logic.

Usage:
  py -3 bankai_client.py --session BANKAI
"""
import argparse
import logging
import sys
import time
import base64
import threading
import tkinter as tk

from relay_client import RelayClient
from optimized_capture import OptimizedRemoteViewer


def main():
    parser = argparse.ArgumentParser(description="bankai client-only viewer")
    parser.add_argument("--session", "-s", required=False, default="BANKAI", help="Session code to join (default: BANKAI)")
    parser.add_argument("--server", default=None, help="WebSocket server URL (wss://...)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="[bankai-client] %(levelname)s: %(message)s")

    server_url = args.server if args.server else "wss://sync-hello.onrender.com"

    root = tk.Tk()
    root.title("Bankai Viewer")
    root.geometry("1200x800")

    # Create a simple frame to host the viewer
    viewer_container = tk.Frame(root)
    viewer_container.pack(fill=tk.BOTH, expand=True)

    # create viewer object (it creates Toplevel when asked)
    class AppWrapper:
        def __init__(self, root):
            self.root = root
            self.relay_client = RelayClient(server_url)
            self.remote_viewer = OptimizedRemoteViewer(self)

    app = AppWrapper(root)

    # Relay callbacks
    def on_screen(data_b64):
        try:
            jpeg_bytes = base64.b64decode(data_b64)
            screen_info = {'type': 'screen', 'data': jpeg_bytes, 'timestamp': time.time()}
            # Ensure update happens on main thread
            def update():
                if not app.remote_viewer.viewer_window:
                    app.remote_viewer.create_viewer_window()
                app.remote_viewer.update_display(screen_info)
            app.root.after(0, update)
        except Exception as e:
            logging.error(f"Failed to handle screen data: {e}")

    def on_input(data):
        logging.info(f"Received input data: {data}")

    def on_conn(status):
        logging.info(f"Connection status: {status}")

    app.relay_client.on_screen_data = on_screen
    app.relay_client.on_input_data = on_input
    app.relay_client.on_connection_change = on_conn

    # Connect in background thread
    def connect_thread():
        ok = app.relay_client.connect_as_client(args.session)
        if not ok:
            logging.error("Failed to join session. Exiting.")
            # exit after short delay to allow logging flush
            time.sleep(1)
            try:
                root.quit()
            except:
                pass
        else:
            # Open viewer window immediately on successful connect so user sees the UI
            def open_viewer():
                try:
                    app.remote_viewer.create_viewer_window()
                except Exception as e:
                    logging.error(f"Failed to open viewer window: {e}")
            app.root.after(0, open_viewer)

    threading.Thread(target=connect_thread, daemon=True).start()

    # Start Tk mainloop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            app.relay_client.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()
