#!/usr/bin/env python3
"""
Registry utilities for SAM/SYSTEM extraction
"""

from pathlib import Path
from typing import Dict, Optional


def get_registry_hive_paths() -> Dict[str, str]:
    """
    Get standard Windows registry hive paths
    
    Returns:
        Dict mapping hive names to file paths
    """
    base_path = r"C:\Windows\System32\config"
    
    return {
        'SAM': f"{base_path}\\SAM",
        'SYSTEM': f"{base_path}\\SYSTEM",
        'SECURITY': f"{base_path}\\SECURITY",
        'SOFTWARE': f"{base_path}\\SOFTWARE"
    }


def verify_hive_exists(hive_name: str) -> bool:
    """
    Verify that a registry hive file exists
    
    Args:
        hive_name: Name of hive (SAM, SYSTEM, SECURITY, SOFTWARE)
        
    Returns:
        bool: True if hive file exists
    """
    hives = get_registry_hive_paths()
    
    if hive_name.upper() not in hives:
        return False
    
    hive_path = Path(hives[hive_name.upper()])
    return hive_path.exists()


def get_hive_size(hive_name: str) -> Optional[int]:
    """
    Get size of registry hive file
    
    Args:
        hive_name: Name of hive
        
    Returns:
        int: Size in bytes or None if not found
    """
    hives = get_registry_hive_paths()
    
    if hive_name.upper() not in hives:
        return None
    
    hive_path = Path(hives[hive_name.upper()])
    
    if hive_path.exists():
        return hive_path.stat().st_size
    
    return None


def validate_extracted_files(sam_file: str, system_file: str) -> Tuple[bool, str]:
    """
    Validate that extracted SAM and SYSTEM files are valid
    
    Args:
        sam_file: Path to SAM file
        system_file: Path to SYSTEM file
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    sam_path = Path(sam_file)
    system_path = Path(system_file)
    
    # Check files exist
    if not sam_path.exists():
        return False, f"SAM file not found: {sam_file}"
    
    if not system_path.exists():
        return False, f"SYSTEM file not found: {system_file}"
    
    # Check file sizes (should be at least a few KB)
    sam_size = sam_path.stat().st_size
    system_size = system_path.stat().st_size
    
    if sam_size < 1024:
        return False, f"SAM file too small: {sam_size} bytes"
    
    if system_size < 1024:
        return False, f"SYSTEM file too small: {system_size} bytes"
    
    return True, "Files valid"


from typing import Tuple
