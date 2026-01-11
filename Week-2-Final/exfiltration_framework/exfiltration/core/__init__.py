"""
Core components for Data Exfiltration Framework
"""

from .file_manager import FileManager, TrackedFile
from .staging_area import StagingArea
from .manifest import Manifest

__all__ = ['FileManager', 'TrackedFile', 'StagingArea', 'Manifest']
