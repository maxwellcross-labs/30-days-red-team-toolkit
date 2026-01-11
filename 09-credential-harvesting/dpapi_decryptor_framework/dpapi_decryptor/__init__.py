#!/usr/bin/env python3
"""
DPAPI Credential Decryption Framework
Professional-grade browser password and credential decryption for authorized red team operations
"""

from .core import DPAPIDecryptor
from .decryptors import (
    ChromeDecryptor,
    EdgeDecryptor,
    FirefoxDecryptor,
    WindowsVaultDecryptor,
    RDPDecryptor,
    list_decryptors,
    get_decryptor_info
)
from .utils import (
    check_admin_privileges,
    check_current_user_context,
    print_privilege_status,
    dpapi_decrypt,
    dpapi_decrypt_string,
    is_dpapi_available
)

__version__ = '1.0.0'
__author__ = '30 Days of Red Team'

__all__ = [
    'DPAPIDecryptor',
    'ChromeDecryptor',
    'EdgeDecryptor',
    'FirefoxDecryptor',
    'WindowsVaultDecryptor',
    'RDPDecryptor',
    'list_decryptors',
    'get_decryptor_info',
    'check_admin_privileges',
    'check_current_user_context',
    'print_privilege_status',
    'dpapi_decrypt',
    'dpapi_decrypt_string',
    'is_dpapi_available'
]
