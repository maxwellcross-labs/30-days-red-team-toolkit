"""
Utility Functions
=================

Common utility functions for the Linux privilege escalation framework.
"""

import os
import subprocess
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple


def get_file_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate hash of a file.

    Args:
        path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hex digest or None on error
    """
    try:
        hasher = hashlib.new(algorithm)

        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)

        return hasher.hexdigest()
    except:
        return None


def is_elf_binary(path: str) -> bool:
    """Check if file is an ELF binary"""
    try:
        with open(path, 'rb') as f:
            magic = f.read(4)
        return magic == b'\x7fELF'
    except:
        return False


def get_binary_info(path: str) -> Dict[str, str]:
    """
    Get detailed information about a binary.

    Args:
        path: Path to the binary

    Returns:
        Dictionary with binary info
    """
    info = {}

    # File command
    try:
        result = subprocess.run(
            ['file', path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            info['type'] = result.stdout.split(':', 1)[1].strip() if ':' in result.stdout else result.stdout
    except:
        pass

    # Strings (first 20 interesting strings)
    try:
        result = subprocess.run(
            ['strings', path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            strings = result.stdout.split('\n')
            # Filter for interesting strings
            interesting = [
                s for s in strings
                if len(s) > 5 and any(kw in s.lower() for kw in
                                      ['password', 'user', 'root', 'shell', 'exec', 'system', '/bin/', '/etc/'])
            ][:20]
            info['interesting_strings'] = interesting
    except:
        pass

    return info


def check_path_writable(path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a path is writable and return the writable component.

    Args:
        path: Path to check

    Returns:
        Tuple of (is_writable, writable_path)
    """
    # Check the path itself
    if os.path.exists(path):
        if os.access(path, os.W_OK):
            return True, path

    # Check parent directories
    path_obj = Path(path)

    for parent in path_obj.parents:
        if parent.exists():
            if os.access(str(parent), os.W_OK):
                return True, str(parent)
            break

    return False, None


def get_process_list() -> List[Dict[str, str]]:
    """
    Get list of running processes.

    Returns:
        List of process dictionaries
    """
    processes = []

    try:
        result = subprocess.run(
            ['ps', 'auxww'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.split('\n')[1:]  # Skip header

            for line in lines:
                if line.strip():
                    parts = line.split(None, 10)

                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': parts[10]
                        })
    except:
        pass

    return processes


def get_root_processes() -> List[Dict[str, str]]:
    """Get processes running as root"""
    processes = get_process_list()
    return [p for p in processes if p.get('user') == 'root']


def find_files_by_permission(
        search_path: str,
        permission: str,
        timeout: int = 60
) -> List[str]:
    """
    Find files with specific permissions.

    Args:
        search_path: Directory to search
        permission: Permission string (e.g., '-4000' for SUID)
        timeout: Search timeout in seconds

    Returns:
        List of file paths
    """
    try:
        result = subprocess.run(
            f"find {search_path} -type f -perm {permission} 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    except:
        pass

    return []


def is_world_writable(path: str) -> bool:
    """Check if file/directory is world-writable"""
    try:
        mode = os.stat(path).st_mode
        return bool(mode & 0o002)
    except:
        return False


def get_kernel_version() -> Optional[str]:
    """Get kernel version"""
    try:
        result = subprocess.run(
            ['uname', '-r'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None


def get_distribution_info() -> Dict[str, str]:
    """Get Linux distribution information"""
    info = {}

    # Try /etc/os-release
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    info[key] = value.strip('"')
    except:
        pass

    # Fallback to lsb_release
    if not info:
        try:
            result = subprocess.run(
                ['lsb_release', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
        except:
            pass

    return info