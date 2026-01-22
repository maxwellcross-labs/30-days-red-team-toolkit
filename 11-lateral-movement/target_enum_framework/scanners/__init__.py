"""
Scanners package for Target Enumeration Framework
Provides factory functions to get protocol scanners
"""

import sys
from pathlib import Path
from typing import Dict, Type, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseScanner
from smb import SMBScanner
from winrm import WinRMScanner
from rdp import RDPScanner
from ssh import SSHScanner

# Scanner registry for factory pattern
SCANNER_REGISTRY: Dict[str, Type[BaseScanner]] = {
    'smb': SMBScanner,
    'winrm': WinRMScanner,
    'rdp': RDPScanner,
    'ssh': SSHScanner
}


def get_scanner(protocol: str, timeout: int = 300) -> BaseScanner:
    """
    Factory function to get scanner by protocol name

    Args:
        protocol: Protocol name ('smb', 'winrm', 'rdp', 'ssh')
        timeout: Scan timeout in seconds

    Returns:
        Configured scanner instance

    Raises:
        ValueError: If protocol is unknown
    """
    protocol = protocol.lower()

    if protocol not in SCANNER_REGISTRY:
        valid_protocols = ', '.join(SCANNER_REGISTRY.keys())
        raise ValueError(f"Unknown protocol: {protocol}. Valid: {valid_protocols}")

    return SCANNER_REGISTRY[protocol](timeout=timeout)


def get_all_scanners(timeout: int = 300) -> List[BaseScanner]:
    """
    Get instances of all available scanners

    Args:
        timeout: Scan timeout for each scanner

    Returns:
        List of scanner instances
    """
    return [scanner_class(timeout=timeout) for scanner_class in SCANNER_REGISTRY.values()]


def list_protocols() -> List[str]:
    """Get list of available protocol names"""
    return list(SCANNER_REGISTRY.keys())


__all__ = [
    'BaseScanner',
    'SMBScanner',
    'WinRMScanner',
    'RDPScanner',
    'SSHScanner',
    'get_scanner',
    'get_all_scanners',
    'list_protocols',
    'SCANNER_REGISTRY'
]