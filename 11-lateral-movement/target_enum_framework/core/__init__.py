"""
Core package for Target Enumeration Framework
"""

from .models import (
    Protocol,
    OperatingSystem,
    TargetCategory,
    HostInfo,
    ScanResult,
    TargetCollection,
    FrameworkConfig,
    HIGH_VALUE_KEYWORDS
)
from .analyzer import HighValueAnalyzer
from .framework import TargetEnumerationFramework

__all__ = [
    'Protocol',
    'OperatingSystem',
    'TargetCategory',
    'HostInfo',
    'ScanResult',
    'TargetCollection',
    'FrameworkConfig',
    'HIGH_VALUE_KEYWORDS',
    'HighValueAnalyzer',
    'TargetEnumerationFramework'
]