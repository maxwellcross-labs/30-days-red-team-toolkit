#!/usr/bin/env python3
"""
Privilege checking utilities for SAM/SYSTEM operations
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


def check_system_privileges() -> bool:
    """
    Check if running as SYSTEM
    Ideal for registry extraction
    
    Returns:
        bool: True if running as SYSTEM
    """
    try:
        import os
        username = os.environ.get('USERNAME', '').upper()
        return username == 'SYSTEM'
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
    is_system = check_system_privileges()
    
    print(f"[*] Privilege Status:")
    print(f"    Administrator: {'✓' if is_admin else '✗'} {msg}")
    print(f"    SYSTEM Context: {'✓' if is_system else '✗'}")
    
    if not is_admin:
        print(f"\n[!] Run as: Administrator or SYSTEM")
        print(f"[!] Example: runas /user:Administrator python sam_extract.py")
        print(f"[!] Or use: PsExec -s -i python sam_extract.py")
