#!/usr/bin/env python3
"""
SAM/SYSTEM Registry Extraction Framework
Professional-grade local account hash harvesting for authorized red team operations
"""

from .core import SAMExtractor
from .methods import (
    RegSaveExtractor,
    VSSExtractor,
    list_methods,
    get_method_info
)
from .parsers import SecretsdumpParser
from .utils import (
    check_admin_privileges,
    check_system_privileges,
    print_privilege_status,
    get_registry_hive_paths,
    validate_extracted_files
)

__version__ = '1.0.0'
__author__ = '30 Days of Red Team'

__all__ = [
    'SAMExtractor',
    'RegSaveExtractor',
    'VSSExtractor',
    'SecretsdumpParser',
    'list_methods',
    'get_method_info',
    'check_admin_privileges',
    'check_system_privileges',
    'print_privilege_status',
    'get_registry_hive_paths',
    'validate_extracted_files'
]
