"""
UAC Bypass Framework
====================

A modular framework for bypassing Windows User Account Control (UAC)
using multiple techniques for different Windows versions.

Features:
    - Multiple UAC bypass techniques
    - Automatic Windows version detection
    - Automatic method selection based on OS
    - Registry-based and environment hijacking
    - OPSEC-conscious cleanup
    - Comprehensive testing and validation

Modules:
    - core: System detection and UAC status checking
    - bypasses: Individual bypass technique implementations
    - utils: Helper functions and reporting

Author: Maxwell Cross
Version: 1.0.0
"""

from .core.detector import SystemDetector
from .core.uac_checker import UACChecker
from .bypasses.fodhelper import FodhelperBypass
from .bypasses.eventvwr import EventvwrBypass
from .bypasses.sdclt import SdcltBypass
from .bypasses.computerdefaults import ComputerDefaultsBypass
from .bypasses.slui import SluiBypass
from .bypasses.diskcleanup import DiskCleanupBypass

__version__ = "1.0.0"
__all__ = [
    "SystemDetector",
    "UACChecker",
    "FodhelperBypass",
    "EventvwrBypass",
    "SdcltBypass",
    "ComputerDefaultsBypass",
    "SluiBypass",
    "DiskCleanupBypass"
]