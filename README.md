# SecureRemote Desktop Application

A legitimate remote desktop application similar to AnyDesk with professional features.

## Features

- ✅ **System Tray Integration** - Minimizes to system tray when hidden
- ✅ **Key-based Authentication** - Secure connection using generated keys
- ✅ **Screen Sharing** - Real-time desktop sharing
- ✅ **Remote Control** - Mouse and keyboard input from remote client
- ✅ **Encrypted Communication** - Secure data transmission
- ✅ **Professional UI** - Clean interface for both server and client modes

## Requirements

- Python 3.8+
- tkinter (GUI)
- Pillow (Screen capture)
- cryptography (Encryption)
- socket (Networking)
- pystray (System tray)
- threading (Multi-threading)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Usage

### Server Mode (Host)
1. Run the application
2. Click "Start Server" to generate a connection key
3. Share the key with the person who needs to connect
4. Use "Hide" button to minimize to system tray

### Client Mode (Connect)
1. Run the application
2. Enter the connection key provided by the host
3. Click "Connect" to establish remote connection

## Security Features

- All connections are encrypted using industry-standard cryptography
- Keys are generated randomly and expire after use
- No persistent backdoors or hidden access
- Full user control and transparency

## Legal Notice

This software is designed for legitimate remote assistance purposes only. 
Users are responsible for ensuring they have proper authorization before 
connecting to any system.
