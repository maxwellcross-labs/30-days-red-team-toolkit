import os
import sys
import subprocess
from typing import Dict


def print_banner():
    """Print the framework banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║     Scheduled Task Exploitation Framework v1.0            ║
║     Windows Privilege Escalation Toolkit                  ║
╠═══════════════════════════════════════════════════════════╣
║  Modules:                                                 ║
║    • Task Enumerator   - Discover all scheduled tasks     ║
║    • Task Analyzer     - Find exploitation opportunities  ║
║    • Script Injector   - Inject payloads into scripts     ║
║    • Task Exploiter    - Orchestrate full exploitation    ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_status():
    """Print current system status."""
    print("\n[*] System Status:")

    # Get current user
    result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
    print(f"    User: {result.stdout.strip()}")

    # Check admin
    is_admin = check_admin()
    print(f"    Administrator: {'Yes' if is_admin else 'No'}")

    # Get hostname
    hostname = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown'))
    print(f"    Hostname: {hostname}")

    # Get domain if available
    domain = os.environ.get('USERDOMAIN', 'N/A')
    print(f"    Domain: {domain}")


def check_admin() -> bool:
    """
    Check if running with administrator privileges.

    Returns:
        True if admin, False otherwise
    """
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    except:
        return False


def check_windows() -> bool:
    """
    Check if running on Windows.

    Returns:
        True if Windows, False otherwise
    """
    return os.name == 'nt'


def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.

    Returns:
        Dictionary with system information
    """
    info = {
        'hostname': os.environ.get('COMPUTERNAME', 'unknown'),
        'username': os.environ.get('USERNAME', 'unknown'),
        'domain': os.environ.get('USERDOMAIN', 'N/A'),
        'is_admin': str(check_admin()),
        'os': 'unknown',
        'version': 'unknown'
    }

    if os.name == 'nt':
        result = subprocess.run(
            'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
            shell=True,
            capture_output=True,
            text=True
        )

        for line in result.stdout.split('\n'):
            if 'OS Name:' in line:
                info['os'] = line.split(':', 1)[1].strip()
            elif 'OS Version:' in line:
                info['version'] = line.split(':', 1)[1].strip()

    return info


def validate_path(path: str) -> bool:
    """
    Validate that a path exists.

    Args:
        path: Path to validate

    Returns:
        True if exists, False otherwise
    """
    return os.path.exists(path)


def format_timestamp(dt) -> str:
    """
    Format a datetime object to string.

    Args:
        dt: Datetime object

    Returns:
        Formatted string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")