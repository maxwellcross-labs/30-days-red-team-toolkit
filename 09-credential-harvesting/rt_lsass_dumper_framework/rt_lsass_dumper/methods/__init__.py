#!/usr/bin/env python3
"""
LSASS dumping methods
Multiple techniques with varying OPSEC profiles
"""

from .comsvcs import ComsvcsDumper
from .procdump import ProcdumpDumper
from .powershell import PowerShellDumper
from .mimikatz import MimikatzDumper
from .nanodump import NanodumpDumper
from .syscalls import SyscallsDumper

__all__ = [
    'ComsvcsDumper',
    'ProcdumpDumper',
    'PowerShellDumper',
    'MimikatzDumper',
    'NanodumpDumper',
    'SyscallsDumper'
]

# Method registry for easy access
DUMPER_REGISTRY = {
    'comsvcs': ComsvcsDumper,
    'procdump': ProcdumpDumper,
    'powershell': PowerShellDumper,
    'mimikatz': MimikatzDumper,
    'nanodump': NanodumpDumper,
    'direct_syscalls': SyscallsDumper
}

def get_dumper(method: str):
    """
    Get dumper class by method name
    
    Args:
        method: Method name (e.g., 'comsvcs', 'procdump')
        
    Returns:
        Dumper class or None if not found
    """
    return DUMPER_REGISTRY.get(method.lower())


def list_methods():
    """List all available dumping methods"""
    return list(DUMPER_REGISTRY.keys())


def get_method_info(method: str):
    """
    Get information about a specific method
    
    Args:
        method: Method name
        
    Returns:
        Dict with method information
    """
    dumper_class = get_dumper(method)
    if dumper_class:
        return dumper_class.get_info()
    return None
