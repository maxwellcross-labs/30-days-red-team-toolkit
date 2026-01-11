#!/usr/bin/env python3
"""
Utility modules for SAM extractor framework
"""

from .privileges import (
    check_admin_privileges,
    check_system_privileges,
    require_admin,
    print_privilege_status
)

from .registry import (
    get_registry_hive_paths,
    verify_hive_exists,
    get_hive_size,
    validate_extracted_files
)

__all__ = [
    'check_admin_privileges',
    'check_system_privileges',
    'require_admin',
    'print_privilege_status',
    'get_registry_hive_paths',
    'verify_hive_exists',
    'get_hive_size',
    'validate_extracted_files'
]
