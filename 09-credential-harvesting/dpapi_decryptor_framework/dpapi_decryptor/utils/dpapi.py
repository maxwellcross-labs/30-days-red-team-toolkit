#!/usr/bin/env python3
"""
DPAPI utilities for credential decryption
"""

from typing import Optional
import base64


def dpapi_decrypt(encrypted_data: bytes, entropy: Optional[bytes] = None) -> Optional[bytes]:
    """
    Decrypt data using Windows DPAPI
    
    Args:
        encrypted_data: Encrypted bytes
        entropy: Optional entropy bytes
        
    Returns:
        Decrypted bytes or None on failure
    """
    try:
        import win32crypt
        
        decrypted = win32crypt.CryptUnprotectData(
            encrypted_data,
            entropy,
            None,
            None,
            0
        )
        
        return decrypted[1]
    
    except ImportError:
        return None
    except Exception:
        return None


def dpapi_decrypt_string(encrypted_data: bytes, encoding: str = 'utf-8') -> Optional[str]:
    """
    Decrypt data and decode as string
    
    Args:
        encrypted_data: Encrypted bytes
        encoding: String encoding
        
    Returns:
        Decrypted string or None on failure
    """
    decrypted = dpapi_decrypt(encrypted_data)
    
    if decrypted:
        try:
            return decrypted.decode(encoding)
        except UnicodeDecodeError:
            try:
                return decrypted.decode('utf-8', errors='ignore')
            except:
                return None
    
    return None


def is_dpapi_available() -> bool:
    """
    Check if DPAPI (pywin32) is available
    
    Returns:
        bool: True if win32crypt is available
    """
    try:
        import win32crypt
        return True
    except ImportError:
        return False


def decode_base64_dpapi(encoded_data: str) -> Optional[bytes]:
    """
    Decode base64 and decrypt with DPAPI
    
    Args:
        encoded_data: Base64 encoded encrypted data
        
    Returns:
        Decrypted bytes or None
    """
    try:
        encrypted = base64.b64decode(encoded_data)
        return dpapi_decrypt(encrypted)
    except:
        return None
