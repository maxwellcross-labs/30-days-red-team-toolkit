"""
Helper Utilities Module
Common utility functions for the UAC bypass framework.
"""

import os
import sys


def print_banner():
    """Print the framework banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║     UAC Bypass Framework v1.0                             ║
║     Windows User Account Control Bypass Toolkit           ║
╠═══════════════════════════════════════════════════════════╣
║  Methods:                                                 ║
║    • Fodhelper        - ms-settings hijacking             ║
║    • Eventvwr         - mscfile hijacking                 ║
║    • Sdclt            - App Paths hijacking               ║
║    • ComputerDefaults - ms-settings hijacking             ║
║    • Slui             - runas command hijacking           ║
║    • DiskCleanup      - Environment variable hijacking    ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_status():
    """Print current system status."""
    from ..core.detector import SystemDetector
    from ..core.uac_checker import UACChecker

    detector = SystemDetector()
    checker = UACChecker()

    detector.print_info()
    checker.print_status()


def check_windows() -> bool:
    """
    Check if running on Windows.

    Returns:
        True if Windows, False otherwise
    """
    return os.name == 'nt'


def check_admin_required() -> bool:
    """
    Check if admin is required and available.

    Returns:
        True if admin and can proceed, False otherwise
    """
    if not check_windows():
        print("[-] This tool only works on Windows systems")
        return False

    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        if not is_admin:
            print("[-] Error: Must run as administrator")
            print("[*] UAC bypass requires administrator privileges")
            print("[*] Use privilege escalation techniques first to gain admin")
            return False

        return True
    except Exception:
        return False


def validate_payload(payload_path: str) -> bool:
    """
    Validate that payload exists.

    Args:
        payload_path: Path to payload

    Returns:
        True if valid, False otherwise
    """
    if not payload_path:
        print("[-] Payload path required")
        return False

    if not os.path.exists(payload_path):
        print(f"[-] Payload not found: {payload_path}")
        return False

    return True