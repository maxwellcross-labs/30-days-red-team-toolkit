#!/usr/bin/env python3
"""
Privilege checking utilities for LSASS operations
"""

import ctypes
import sys
from typing import Tuple


def check_admin_privileges() -> Tuple[bool, str]:
    """
    Check if running with administrative privileges
    
    Returns:
        Tuple of (is_admin: bool, message: str)
    """
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        
        if is_admin:
            return True, "Running with administrative privileges"
        else:
            return False, "Administrative privileges required"
    
    except Exception as e:
        return False, f"Could not verify privileges: {e}"


def check_debug_privilege() -> bool:
    """
    Check if SeDebugPrivilege is available
    Required for LSASS access
    
    Returns:
        bool: True if debug privilege available
    """
    try:
        # This is a placeholder - actual implementation would check token privileges
        # For now, assume if admin, debug privilege is available
        is_admin, _ = check_admin_privileges()
        return is_admin
    
    except Exception:
        return False


def require_admin(func):
    """
    Decorator to require admin privileges for a function
    """
    def wrapper(*args, **kwargs):
        is_admin, msg = check_admin_privileges()
        
        if not is_admin:
            print(f"[-] ERROR: {msg}")
            print(f"[!] This operation requires administrative privileges")
            return None
        
        return func(*args, **kwargs)
    
    return wrapper


def print_privilege_status():
    """Print current privilege status"""
    is_admin, msg = check_admin_privileges()
    has_debug = check_debug_privilege()
    
    print(f"[*] Privilege Status:")
    print(f"    Administrator: {'✓' if is_admin else '✗'} {msg}")
    print(f"    Debug Privilege: {'✓' if has_debug else '✗'}")
    
    if not is_admin:
        print(f"\n[!] Run as: Administrator or SYSTEM")
        print(f"[!] Example: runas /user:Administrator python lsass_dump.py")
