#!/usr/bin/env python3
"""
Registry access utilities
"""

import winreg
from typing import Optional, Dict, List, Tuple, Any


def safe_open_key(root: int, path: str, access: int = winreg.KEY_READ) -> Optional[winreg.HKEYType]:
    """
    Safely open a registry key
    
    Args:
        root: Registry root (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
        path: Registry key path
        access: Access rights
        
    Returns:
        Registry key handle or None on failure
    """
    try:
        return winreg.OpenKey(root, path, 0, access)
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except Exception:
        return None


def safe_query_value(key: winreg.HKEYType, value_name: str) -> Optional[Tuple]:
    """
    Safely query a registry value
    
    Args:
        key: Registry key handle
        value_name: Value name to query
        
    Returns:
        Tuple of (value, type) or None on failure
    """
    try:
        return winreg.QueryValueEx(key, value_name)
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except Exception:
        return None


def enumerate_subkeys(key: winreg.HKEYType) -> List[str]:
    """
    Enumerate all subkeys under a registry key
    
    Args:
        key: Registry key handle
        
    Returns:
        List of subkey names
    """
    subkeys = []
    i = 0
    
    while True:
        try:
            subkey_name = winreg.EnumKey(key, i)
            subkeys.append(subkey_name)
            i += 1
        except OSError:
            break
    
    return subkeys


def read_registry_value(root: int, path: str, value_name: str) -> Optional[Any]:
    """
    Read a single registry value
    
    Args:
        root: Registry root
        path: Registry key path
        value_name: Value name
        
    Returns:
        Value data or None
    """
    key = safe_open_key(root, path)
    
    if not key:
        return None
    
    try:
        result = safe_query_value(key, value_name)
        return result[0] if result else None
    finally:
        winreg.CloseKey(key)


def read_all_values(root: int, path: str) -> Dict[str, any]:
    """
    Read all values from a registry key
    
    Args:
        root: Registry root
        path: Registry key path
        
    Returns:
        Dictionary of value names to values
    """
    key = safe_open_key(root, path)
    
    if not key:
        return {}
    
    values = {}
    i = 0
    
    try:
        while True:
            try:
                value_name, value_data, value_type = winreg.EnumValue(key, i)
                values[value_name] = value_data
                i += 1
            except OSError:
                break
    finally:
        winreg.CloseKey(key)
    
    return values


def key_exists(root: int, path: str) -> bool:
    """
    Check if a registry key exists
    
    Args:
        root: Registry root
        path: Registry key path
        
    Returns:
        bool: True if key exists
    """
    key = safe_open_key(root, path)
    
    if key:
        winreg.CloseKey(key)
        return True
    
    return False
