#!/usr/bin/env python3
"""
Encryption Module
Handles file encryption for secure exfiltration
"""

import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional


class FileEncryptor:
    """
    Encrypts files for secure exfiltration
    Uses Fernet (AES-128) symmetric encryption
    """
    
    def __init__(self):
        """Initialize encryptor"""
        self.algorithm = "Fernet (AES-128)"
    
    def generate_key(self) -> bytes:
        """
        Generate encryption key
        
        Returns:
            Encryption key bytes
        """
        try:
            from cryptography.fernet import Fernet
            return Fernet.generate_key()
        except ImportError:
            # Fallback to basic XOR if cryptography not available
            return os.urandom(32)
    
    def encrypt_file(self, input_path: Path, output_path: Path, key: bytes = None) -> Tuple[Path, bytes]:
        """
        Encrypt a file
        
        Args:
            input_path: Path to input file
            output_path: Path for encrypted output
            key: Encryption key (generated if not provided)
            
        Returns:
            Tuple of (output_path, encryption_key)
        """
        # Generate key if not provided
        if key is None:
            key = self.generate_key()
        
        try:
            from cryptography.fernet import Fernet
            
            cipher = Fernet(key)
            
            # Read and encrypt
            with open(input_path, 'rb') as f:
                plaintext = f.read()
            
            encrypted_data = cipher.encrypt(plaintext)
            
            # Write encrypted data
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
        
        except ImportError:
            # Fallback XOR encryption
            self._xor_encrypt_file(input_path, output_path, key)
        
        return output_path, key
    
    def _xor_encrypt_file(self, input_path: Path, output_path: Path, key: bytes) -> None:
        """
        Simple XOR encryption fallback
        
        Args:
            input_path: Path to input file
            output_path: Path for encrypted output
            key: Encryption key
        """
        with open(input_path, 'rb') as f_in:
            data = f_in.read()
        
        # XOR encryption
        key_len = len(key)
        encrypted = bytes([data[i] ^ key[i % key_len] for i in range(len(data))])
        
        with open(output_path, 'wb') as f_out:
            f_out.write(encrypted)
    
    def decrypt_file(self, input_path: Path, output_path: Path, key: bytes) -> Path:
        """
        Decrypt a file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted output
            key: Encryption key
            
        Returns:
            Path to decrypted file
        """
        try:
            from cryptography.fernet import Fernet
            
            cipher = Fernet(key)
            
            # Read and decrypt
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Write decrypted data
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
        
        except ImportError:
            # Fallback XOR decryption (same as encryption)
            self._xor_encrypt_file(input_path, output_path, key)
        
        return output_path
    
    def save_key(self, key: bytes, output_path: Path) -> None:
        """
        Save encryption key to file
        
        Args:
            key: Encryption key
            output_path: Path to save key
        """
        with open(output_path, 'wb') as f:
            f.write(key)
    
    def load_key(self, key_path: Path) -> bytes:
        """
        Load encryption key from file
        
        Args:
            key_path: Path to key file
            
        Returns:
            Encryption key bytes
        """
        with open(key_path, 'rb') as f:
            return f.read()
