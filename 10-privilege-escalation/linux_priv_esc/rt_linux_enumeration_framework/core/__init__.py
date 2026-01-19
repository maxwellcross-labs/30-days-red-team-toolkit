"""
Core Module
===========

Core components for the Linux privilege escalation framework.
"""

from .findings import Finding, FindingSeverity, FindingsCollection
from .config import Config
from .base import BaseEnumerator

__all__ = [
    'Finding',
    'FindingSeverity',
    'FindingsCollection',
    'Config',
    'BaseEnumerator'
]
