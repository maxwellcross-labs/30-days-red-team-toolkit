#!/usr/bin/env python3
"""
Privilege checking utilities for registry mining operations
"""

import ctypes
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
            return False, "User-level access only"
    
    except Exception as e:
        return False, f"Could not verify privileges: {e}"


def check_system_privileges() -> bool:
    """
    Check if running as SYSTEM
    
    Returns:
        bool: True if running as SYSTEM
    """
    try:
        import os
        username = os.environ.get('USERNAME', '').upper()
        return username == 'SYSTEM'
    except Exception:
        return False


def print_privilege_status():
    """Print current privilege status"""
    is_admin, msg = check_admin_privileges()
    is_system = check_system_privileges()
    
    print(f"[*] Privilege Status:")
    print(f"    Administrator: {'✓' if is_admin else '✗'} {msg}")
    print(f"    SYSTEM Context: {'✓' if is_system else '✗'}")
    
    if not is_admin:
        print(f"\n[!] Note: Some registry keys require administrative privileges")
        print(f"[!] LSA Secrets and cached credentials require SYSTEM privileges")
        print(f"[*] User-level credentials will still be extracted")
