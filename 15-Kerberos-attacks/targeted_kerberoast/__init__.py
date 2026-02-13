"""
Targeted Kerberoasting — Surgical precision, minimal noise.
Single-user and prioritized roasting with OPSEC-aware delays.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

from .core.roaster import TargetedKerberoast

__all__ = ["TargetedKerberoast"]