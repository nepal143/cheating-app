"""
Cryptography Module
Handles encryption and decryption for secure communications.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import secrets

class CryptoManager:
    def __init__(self):
        self.fernet = None
        self.key = None
        
    def generate_key(self):
        """Generate a new encryption key"""
        key = Fernet.generate_key()
        self.set_key(key)
        return key
        
    def set_key(self, key):
        """Set the encryption key"""
        self.key = key
        self.fernet = Fernet(key)
        
    def encrypt(self, data):
        """Encrypt data"""
        if not self.fernet:
            raise ValueError("No encryption key set")
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return self.fernet.encrypt(data)
        
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        if not self.fernet:
            raise ValueError("No encryption key set")
            
        decrypted = self.fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
        
    def derive_key_from_password(self, password, salt=None):
        """Derive encryption key from password"""
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.set_key(key)
        return key, salt
        
    def generate_session_token(self):
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
        
    def verify_session_token(self, token):
        """Verify session token format"""
        try:
            # Basic verification - check if it's a valid base64 string
            decoded = base64.urlsafe_b64decode(token + '==')  # Add padding if needed
            return len(decoded) >= 24  # Minimum 24 bytes for security
        except:
            return False
