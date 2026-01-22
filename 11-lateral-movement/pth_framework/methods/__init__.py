"""
Authentication methods package for Pass-the-Hash Framework
Provides factory function to get appropriate auth method
"""

import sys
from pathlib import Path
from typing import Dict, Type

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import BaseAuthMethod
from .smb import SMBAuthMethod
from .wmi import WMIAuthMethod
from .psexec import PSExecAuthMethod
from .rdp import RDPAuthMethod

# Method registry for factory pattern
METHOD_REGISTRY: Dict[str, Type[BaseAuthMethod]] = {
    'smb': SMBAuthMethod,
    'wmi': WMIAuthMethod,
    'psexec': PSExecAuthMethod,
    'rdp': RDPAuthMethod
}


def get_auth_method(method_name: str, timeout: int = 30) -> BaseAuthMethod:
    """
    Factory function to get authentication method by name

    Args:
        method_name: Name of method ('smb', 'wmi', 'psexec', 'rdp')
        timeout: Command execution timeout

    Returns:
        Configured authentication method instance

    Raises:
        ValueError: If method name is unknown
    """
    method_name = method_name.lower()

    if method_name not in METHOD_REGISTRY:
        valid_methods = ', '.join(METHOD_REGISTRY.keys())
        raise ValueError(f"Unknown method: {method_name}. Valid: {valid_methods}")

    return METHOD_REGISTRY[method_name](timeout=timeout)


def list_methods() -> list:
    """Get list of available method names"""
    return list(METHOD_REGISTRY.keys())


__all__ = [
    'BaseAuthMethod',
    'SMBAuthMethod',
    'WMIAuthMethod',
    'PSExecAuthMethod',
    'RDPAuthMethod',
    'get_auth_method',
    'list_methods',
    'METHOD_REGISTRY'
]