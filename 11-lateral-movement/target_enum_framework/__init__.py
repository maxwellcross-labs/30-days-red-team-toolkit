"""
Target Enumeration Framework

A modular framework for discovering lateral movement targets
during authorized penetration testing and red team operations.

Supported Protocols:
    - SMB (port 445) - Primary Windows lateral movement
    - WinRM (port 5985/5986) - PowerShell Remoting
    - RDP (port 3389) - Remote Desktop
    - SSH (port 22) - Linux lateral movement

Features:
    - Multi-protocol scanning
    - High-value target identification
    - Automatic categorization (Windows/Linux/DCs)
    - Target list generation for tools
    - Comprehensive JSON reporting

Basic Usage:
    from target_enum_framework import TargetEnumerationFramework

    framework = TargetEnumerationFramework()

    # Full auto enumeration
    collection = framework.auto_enumerate("192.168.1.0/24")

    # Get target lists
    windows = framework.get_targets('windows')
    high_value = framework.get_targets('high_value')

    # Or scan specific protocols
    collection = framework.scan_protocols(
        "192.168.1.0/24",
        protocols=["smb", "winrm"]
    )

CLI Usage:
    python -m target_enum_framework --network 192.168.1.0/24

Author: Maxwell Cross
Purpose: Authorized penetration testing and red team operations only.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

# Core exports
from .core import (
    TargetEnumerationFramework,
    TargetCollection,
    HostInfo,
    ScanResult,
    FrameworkConfig,
    Protocol,
    OperatingSystem,
    TargetCategory,
    HighValueAnalyzer,
    HIGH_VALUE_KEYWORDS
)

# Scanner exports
from .scanners import (
    get_scanner,
    get_all_scanners,
    list_protocols,
    SMBScanner,
    WinRMScanner,
    RDPScanner,
    SSHScanner
)

# Report exports
from .reports import (
    ReportGenerator
)

# Utility exports
from .utils import (
    is_valid_ip,
    extract_ips_from_text,
    parse_network_range,
    load_targets_from_file
)

__all__ = [
    # Version
    '__version__',
    '__author__',

    # Core
    'TargetEnumerationFramework',
    'TargetCollection',
    'HostInfo',
    'ScanResult',
    'FrameworkConfig',
    'Protocol',
    'OperatingSystem',
    'TargetCategory',
    'HighValueAnalyzer',
    'HIGH_VALUE_KEYWORDS',

    # Scanners
    'get_scanner',
    'get_all_scanners',
    'list_protocols',
    'SMBScanner',
    'WinRMScanner',
    'RDPScanner',
    'SSHScanner',

    # Reports
    'ReportGenerator',

    # Utilities
    'is_valid_ip',
    'extract_ips_from_text',
    'parse_network_range',
    'load_targets_from_file'
]