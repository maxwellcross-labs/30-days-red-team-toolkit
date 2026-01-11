#!/usr/bin/env python3
"""
Privilege checking utilities for DPAPI decryption operations
"""

import ctypes
import os
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
            return False, "Running with user-level access"
    
    except Exception as e:
        return False, f"Could not verify privileges: {e}"


def check_current_user_context() -> str:
    """
    Get current user context
    DPAPI can only decrypt data encrypted by the same user
    
    Returns:
        str: Current username
    """
    try:
        return os.environ.get('USERNAME', 'Unknown')
    except Exception:
        return 'Unknown'


def print_privilege_status():
    """Print current privilege status"""
    is_admin, msg = check_admin_privileges()
    username = check_current_user_context()
    
    print(f"[*] Privilege Status:")
    print(f"    User Context: {username}")
    print(f"    Administrator: {'✓' if is_admin else '✗'} {msg}")
    
    print(f"\n[!] Important: DPAPI can only decrypt data encrypted by {username}")
    print(f"[!] Browser passwords and credentials belong to the current user")
