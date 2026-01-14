import os
import sys
import subprocess
from typing import Dict, Optional


def print_banner():
    """Print the framework banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║     AlwaysInstallElevated Exploitation Framework v1.0     ║
║     MSI-Based Privilege Escalation Toolkit                ║
╠═══════════════════════════════════════════════════════════╣
║  Modules:                                                 ║
║    • Registry Checker  - Detect misconfiguration          ║
║    • MSI Exploiter     - Install malicious packages       ║
║    • Msfvenom Payloads - Generate reverse shells          ║
║    • WiX Payloads      - Custom MSI generation            ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_status():
    """Print current system status."""
    print("\n[*] System Status:")

    # Get current user
    result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
    print(f"    User: {result.stdout.strip()}")

    # Check if admin
    if os.name == 'nt':
        result = subprocess.run(
            "whoami /groups | findstr /i \"S-1-5-32-544\"",
            shell=True,
            capture_output=True,
            text=True
        )
        is_admin = "S-1-5-32-544" in result.stdout
    else:
        is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    print(f"    Administrator: {'Yes' if is_admin else 'No'}")

    # Get hostname
    hostname = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown'))
    print(f"    Hostname: {hostname}")


def check_tool_available(tool_name: str) -> bool:
    """
    Check if a tool is available on the system.

    Args:
        tool_name: Name of the tool to check

    Returns:
        True if available, False otherwise
    """
    cmd = "where" if os.name == 'nt' else "which"
    result = subprocess.run(f"{cmd} {tool_name}", shell=True, capture_output=True)
    return result.returncode == 0


def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.

    Returns:
        Dictionary with system information
    """
    info = {
        'os': 'unknown',
        'version': 'unknown',
        'architecture': 'unknown',
        'hostname': os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown'))
    }

    if os.name == 'nt':
        result = subprocess.run(
            'systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"',
            shell=True,
            capture_output=True,
            text=True
        )

        for line in result.stdout.split('\n'):
            if 'OS Name:' in line:
                info['os'] = line.split(':', 1)[1].strip()
            elif 'OS Version:' in line:
                info['version'] = line.split(':', 1)[1].strip()
            elif 'System Type:' in line:
                info['architecture'] = 'x64' if 'x64' in line else 'x86'

    return info


def get_msi_error_message(code: int) -> str:
    """
    Get human-readable MSI error message.

    Args:
        code: MSI return code

    Returns:
        Error message string
    """
    from .constants import MSI_ERROR_CODES
    return MSI_ERROR_CODES.get(code, f"Unknown error code: {code}")


def validate_ip(ip: str) -> bool:
    """
    Validate an IP address format.

    Args:
        ip: IP address string

    Returns:
        True if valid, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False

    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False

    return True


def validate_port(port: int) -> bool:
    """
    Validate a port number.

    Args:
        port: Port number

    Returns:
        True if valid, False otherwise
    """
    return 1 <= port <= 65535


def format_size(size_bytes: int) -> str:
    """
    Format byte size to human readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"