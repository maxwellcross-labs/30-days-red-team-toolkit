#!/usr/bin/env python3
"""
Registry credential miners
Different miners for various credential sources
"""

from .autologon import AutoLogonMiner
from .rdp import RDPMiner
from .wifi import WiFiMiner
from .putty import PuTTYMiner
from .vnc import VNCMiner
from .winscp import WinSCPMiner
from .lsa_secrets import LSASecretsMiner

__all__ = [
    'AutoLogonMiner',
    'RDPMiner',
    'WiFiMiner',
    'PuTTYMiner',
    'VNCMiner',
    'WinSCPMiner',
    'LSASecretsMiner'
]

# Miner registry for easy access
# Note: LSASecretsMiner requires output_dir parameter, so it's handled separately in core.py
MINER_REGISTRY = {
    'autologon': AutoLogonMiner,
    'rdp': RDPMiner,
    'wifi': WiFiMiner,
    'putty': PuTTYMiner,
    'vnc': VNCMiner,
    'winscp': WinSCPMiner
}

def get_miner(miner_name: str):
    """
    Get miner class by name
    
    Args:
        miner_name: Miner name
        
    Returns:
        Miner class or None if not found
    """
    return MINER_REGISTRY.get(miner_name.lower())


def list_miners():
    """List all available miners"""
    # Include lsa_secrets even though it needs special handling
    return list(MINER_REGISTRY.keys()) + ['lsa_secrets']


def get_miner_info(miner_name: str):
    """
    Get information about a specific miner
    
    Args:
        miner_name: Miner name
        
    Returns:
        Dict with miner information
    """
    # Handle LSA secrets separately
    if miner_name.lower() == 'lsa_secrets':
        return LSASecretsMiner.get_info()
    
    miner_class = get_miner(miner_name)
    if miner_class:
        return miner_class.get_info()
    return None
