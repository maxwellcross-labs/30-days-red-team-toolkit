#!/usr/bin/env python3
"""
SAM/SYSTEM extraction methods
Different techniques with varying OPSEC profiles
"""

from .reg_save import RegSaveExtractor
from .vss import VSSExtractor

__all__ = [
    'RegSaveExtractor',
    'VSSExtractor'
]

# Method registry for easy access
EXTRACTOR_REGISTRY = {
    'reg_save': RegSaveExtractor,
    'vss': VSSExtractor
}

def get_extractor(method: str):
    """
    Get extractor class by method name
    
    Args:
        method: Method name (e.g., 'reg_save', 'vss')
        
    Returns:
        Extractor class or None if not found
    """
    return EXTRACTOR_REGISTRY.get(method.lower())


def list_methods():
    """List all available extraction methods"""
    return list(EXTRACTOR_REGISTRY.keys())


def get_method_info(method: str):
    """
    Get information about a specific method
    
    Args:
        method: Method name
        
    Returns:
        Dict with method information
    """
    extractor_class = get_extractor(method)
    if extractor_class:
        return extractor_class.get_info()
    return None
