"""
Kerberoasting & AS-REP Roasting Framework
Automated service account hash extraction for offline cracking
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

from .core.target import RoastingTarget
from .core.framework import KerberoastFramework

__all__ = ["RoastingTarget", "KerberoastFramework"]