#!/usr/bin/env python3
"""
DPAPI credential decryptors
Different decryptors for various credential sources
"""

from .chrome import ChromeDecryptor
from .edge import EdgeDecryptor
from .firefox import FirefoxDecryptor
from .windows_vault import WindowsVaultDecryptor
from .rdp import RDPDecryptor

__all__ = [
    'ChromeDecryptor',
    'EdgeDecryptor',
    'FirefoxDecryptor',
    'WindowsVaultDecryptor',
    'RDPDecryptor'
]

# Decryptor registry for easy access
# Note: Some decryptors require output_dir parameter
DECRYPTOR_REGISTRY = {
    'chrome': ChromeDecryptor,
    'edge': EdgeDecryptor,
    'firefox': FirefoxDecryptor,
    'windows_vault': WindowsVaultDecryptor,
    'rdp': RDPDecryptor
}

def get_decryptor(decryptor_name: str):
    """
    Get decryptor class by name
    
    Args:
        decryptor_name: Decryptor name
        
    Returns:
        Decryptor class or None if not found
    """
    return DECRYPTOR_REGISTRY.get(decryptor_name.lower())


def list_decryptors():
    """List all available decryptors"""
    return list(DECRYPTOR_REGISTRY.keys())


def get_decryptor_info(decryptor_name: str):
    """
    Get information about a specific decryptor
    
    Args:
        decryptor_name: Decryptor name
        
    Returns:
        Dict with decryptor information
    """
    decryptor_class = get_decryptor(decryptor_name)
    if decryptor_class:
        return decryptor_class.get_info()
    return None
