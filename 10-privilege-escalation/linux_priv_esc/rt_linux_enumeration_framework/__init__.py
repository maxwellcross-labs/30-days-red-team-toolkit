"""
RT Linux Privilege Escalation Framework
=======================================

Modular automated discovery and exploitation of Linux privilege escalation vectors.

Part of the 30 Days of Red Team toolkit.

Author: Red Team Operator
License: Educational Use Only
"""

__version__ = "1.0.0"
__author__ = "Red Team Operator"
__series__ = "30 Days of Red Team"

from .core.enumerator import LinuxPrivEscEnumerator
from .core.findings import Finding, FindingSeverity
from .core.config import Config

__all__ = [
    'LinuxPrivEscEnumerator',
    'Finding',
    'FindingSeverity',
    'Config'
]
