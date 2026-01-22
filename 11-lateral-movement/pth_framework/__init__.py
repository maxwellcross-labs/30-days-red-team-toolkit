"""
Pass-the-Hash Lateral Movement Framework

A modular framework for NTLM Pass-the-Hash attacks during
authorized penetration testing and red team operations.

Supported Methods:
    - SMB via CrackMapExec (most versatile)
    - WMI via Impacket wmiexec
    - PSExec via Impacket psexec
    - RDP via xfreerdp (requires Restricted Admin)

Basic Usage:
    from pth_framework import PassTheHashFramework, Credential

    framework = PassTheHashFramework()
    credential = Credential("admin", "aad3b435b51404eeaad3b435b51404ee", "CORP")

    # Single target
    result = framework.authenticate("192.168.1.100", credential, method="smb")

    # Spray across targets
    results = framework.spray_hash(
        targets=["192.168.1.100", "192.168.1.101"],
        credential=credential,
        method="smb"
    )

    # Generate report
    framework.generate_report()

CLI Usage:
    python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --method smb

Author: Maxwell Cross
Purpose: Authorized penetration testing and red team operations only.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

# Core exports
from .core import (
    PassTheHashFramework,
    Credential,
    AuthResult,
    SprayResult,
    FrameworkConfig,
    AuthMethod,
    AccessLevel
)

# Method exports
from .methods import (
    get_auth_method,
    list_methods,
    SMBAuthMethod,
    WMIAuthMethod,
    PSExecAuthMethod,
    RDPAuthMethod
)

# Report exports
from .reports import (
    ReportGenerator,
    SprayReporter
)

# Utility exports
from .utils import (
    load_targets_from_file,
    load_credentials_from_file,
    load_hashes_file
)

__all__ = [
    # Version
    '__version__',
    '__author__',

    # Core
    'PassTheHashFramework',
    'Credential',
    'AuthResult',
    'SprayResult',
    'FrameworkConfig',
    'AuthMethod',
    'AccessLevel',

    # Methods
    'get_auth_method',
    'list_methods',
    'SMBAuthMethod',
    'WMIAuthMethod',
    'PSExecAuthMethod',
    'RDPAuthMethod',

    # Reports
    'ReportGenerator',
    'SprayReporter',

    # Utilities
    'load_targets_from_file',
    'load_credentials_from_file',
    'load_hashes_file'
]