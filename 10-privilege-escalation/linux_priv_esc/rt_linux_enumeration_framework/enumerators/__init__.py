"""
Enumerators Module
==================

Individual enumeration modules for different privilege escalation vectors.
"""

from .privileges import PrivilegesEnumerator
from .suid import SUIDEnumerator
from .sudo import SudoEnumerator
from .cron import CronEnumerator
from .writable import WritableFilesEnumerator
from .capabilities import CapabilitiesEnumerator
from .containers import ContainersEnumerator
from .nfs import NFSEnumerator

__all__ = [
    'PrivilegesEnumerator',
    'SUIDEnumerator',
    'SudoEnumerator',
    'CronEnumerator',
    'WritableFilesEnumerator',
    'CapabilitiesEnumerator',
    'ContainersEnumerator',
    'NFSEnumerator'
]

# Registry of all enumerators for easy iteration
ENUMERATOR_CLASSES = [
    PrivilegesEnumerator,
    SUIDEnumerator,
    SudoEnumerator,
    CronEnumerator,
    WritableFilesEnumerator,
    CapabilitiesEnumerator,
    ContainersEnumerator,
    NFSEnumerator
]