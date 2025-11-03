#!/usr/bin/env python3
"""
bankai - Headless client-only runner for IgniteRemote (no GUI)

Usage:
  python bankai.py --session <SESSION_ID> [--server wss://...] [--out-dir ./frames] [-v]

This script connects as a client (viewer) to the relay server and writes
incoming screen frames to disk (overwriting the latest file). It deliberately
does not create any GUI; it's suitable to package as a single-file executable
named `bankai.exe`.
"""
import argparse
import base64
import os
import sys
import time
import logging
from io import BytesIO

from relay_client import RelayClient
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def write_frame_png(out_dir: str, data_b64: str):
    """Decode base64 JPEG bytes and save as PNG (latest_frame.png)."""
    try:
        data = base64.b64decode(data_b64)
        if PIL_AVAILABLE:
            img = Image.open(BytesIO(data))
            path = os.path.join(out_dir, "latest_frame.png")
            img.save(path, format="PNG")
            logging.info(f"Wrote latest frame PNG to: {path} (size={os.path.getsize(path)} bytes)")
        else:
            # Fallback: write raw bytes
            path = os.path.join(out_dir, "latest_frame.bin")
            with open(path, "wb") as f:
                f.write(data)
            logging.info(f"Pillow not available; wrote raw frame to: {path} (size={len(data)} bytes)")
    except Exception as e:
        logging.error(f"Failed to write frame: {e}")


def main():
    parser = argparse.ArgumentParser(description="bankai - headless client runner")
    parser.add_argument("--session", "-s", required=False, default="BANKAI", help="Session ID to join (default: BANKAI)")
    parser.add_argument("--server", default=None, help="WebSocket server URL (wss://...)")
    parser.add_argument("--out-dir", default="./bankai_frames", help="Directory to save incoming frames")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.quiet:
        log_level = logging.ERROR

    logging.basicConfig(level=log_level, format="[bankai] %(levelname)s: %(message)s")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    server_url = args.server if args.server else "wss://sync-hello.onrender.com"

    logging.info(f"Starting bankai client -> session={args.session} server={server_url}")

    relay = RelayClient(server_url)

    # Callbacks
    def on_screen(data_b64):
        # Save frame to disk as PNG (or raw fallback)
        write_frame_png(out_dir, data_b64)

    def on_input(data):
        logging.info(f"Received input data: {data}")

    def on_conn(status):
        logging.info(f"Connection status: {status}")

    relay.on_screen_data = on_screen
    relay.on_input_data = on_input
    relay.on_connection_change = on_conn

    # Connect as client
    # Try to connect with a few retries (networks can be flaky)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        ok = relay.connect_as_client(args.session)
        if ok:
            break
        logging.warning(f"Connect attempt {attempt} failed. Retrying...")
        time.sleep(2 * attempt)

    if not ok:
        logging.error("Failed to connect as client after retries. Exiting.")
        sys.exit(2)

    logging.info("Connected. Running headless receive loop. Press Ctrl-C to exit.")

    try:
        while True:
            time.sleep(5)
            # keepalive ping if connection established
            try:
                relay.ping()
            except Exception:
                # ignore ping failures silently
                pass
    except KeyboardInterrupt:
        logging.info("Interrupted, disconnecting...")
        relay.disconnect()


if __name__ == "__main__":
    main()
