#!/usr/bin/env python3
"""
bankai_auto_connect.py - Auto-connects to any active BANKAI session
This script automatically finds and connects to the current BANKAI session
"""
import sys
import time
import os
import tkinter as tk
from tkinter import messagebox
from optimized_capture import OptimizedRemoteViewer
from relay_client import RelayClient


def find_session_id():
    """Find the current session ID from the session file"""
    try:
        if os.path.exists("bankai_session.txt"):
            with open("bankai_session.txt", "r", encoding='utf-8') as f:
                session_id = f.read().strip()
                if session_id:
                    return session_id
    except:
        pass
    return None


def main():
    print("🔍 Looking for BANKAI session...")
    
    # Look for session file
    session_id = find_session_id()
    if not session_id:
        print("❌ No BANKAI session found. Make sure the host is running.")
        print("💡 Start the host first with: py -3 bankai_force_host.py")
        return
    
    print(f"📡 Found session: {session_id}")
    print(f"🚀 Connecting to session {session_id}...")
    
    relay = RelayClient("wss://sync-hello.onrender.com")
    
    # Check if session exists
    if not relay.join_session(session_id):
        print(f"❌ Session {session_id} not found or expired")
        print("💡 Restart the host to create a new session")
        return
    
    print(f"✅ Session {session_id} found!")
    
    # Connect as client
    if not relay.connect_as_client(session_id):
        print("❌ Failed to connect as client")
        return
    
    print("✅ Connected as client!")
    print("🖥️ Opening viewer window...")
    
    # Create viewer
    viewer = OptimizedRemoteViewer()
    
    # Set up callbacks
    def on_screen_data(data):
        try:
            viewer.update_screen(data)
        except Exception as e:
            print(f"Viewer error: {e}")
    
    def on_input_data(data):
        pass  # Client doesn't send input in this setup
    
    def on_connection_change(status):
        print(f"Connection status: {status}")
        if status == "disconnected":
            print("🔌 Disconnected from host")
    
    relay.on_screen_data = on_screen_data
    relay.on_input_data = on_input_data
    relay.on_connection_change = on_connection_change
    
    # Show viewer
    viewer.show()
    
    print("📺 Viewer is now showing remote screen!")
    print("Press Ctrl+C to exit")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down viewer...")
    finally:
        relay.disconnect()
        viewer.close()


if __name__ == "__main__":
    main()