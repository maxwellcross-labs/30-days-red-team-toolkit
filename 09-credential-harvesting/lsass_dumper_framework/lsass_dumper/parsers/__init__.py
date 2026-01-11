#!/usr/bin/env python3
"""
LSASS dump parsers for credential extraction
"""

from .pypykatz_parser import PyPykatzParser

__all__ = [
    'PyPykatzParser'
]
