"""
Data Exfiltration Framework
Professional-grade secure data exfiltration for authorized red team operations
"""

from .core.file_manager import FileManager
from .core.staging_area import StagingArea
from .core.manifest import Manifest
from .handlers.exfiltration_handler import ExfiltrationHandler

__version__ = "1.0.0"
__author__ = "Red Team Operations"

__all__ = [
    'FileManager',
    'StagingArea',
    'Manifest',
    'ExfiltrationHandler'
]
