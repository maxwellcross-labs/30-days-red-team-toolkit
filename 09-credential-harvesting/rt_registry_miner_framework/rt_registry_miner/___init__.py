#!/usr/bin/env python3
"""
Registry Credential Mining Framework
Professional-grade credential extraction from Windows registry for authorized red team operations
"""

from .core import RegistryCredentialMiner
from .miners import (
    AutoLogonMiner,
    RDPMiner,
    WiFiMiner,
    PuTTYMiner,
    VNCMiner,
    WinSCPMiner,
    LSASecretsMiner,
    list_miners,
    get_miner_info
)
from .utils import (
    check_admin_privileges,
    check_system_privileges,
    print_privilege_status
)

__version__ = '1.0.0'
__author__ = '30 Days of Red Team'

__all__ = [
    'RegistryCredentialMiner',
    'AutoLogonMiner',
    'RDPMiner',
    'WiFiMiner',
    'PuTTYMiner',
    'VNCMiner',
    'WinSCPMiner',
    'LSASecretsMiner',
    'list_miners',
    'get_miner_info',
    'check_admin_privileges',
    'check_system_privileges',
    'print_privilege_status'
]
