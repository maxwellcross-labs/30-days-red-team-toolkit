"""
File utilities for Remote Execution Framework
Handles loading targets, credentials, and file operations
"""

import sys
import json
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..core.models import Credential


def load_targets_from_file(filepath: str) -> List[str]:
    """
    Load target IPs/hostnames from file

    Args:
        filepath: Path to file with one target per line

    Returns:
        List of target strings
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Target file not found: {filepath}")

    with open(path, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]

    return targets


def load_credentials_from_file(filepath: str) -> List[Credential]:
    """
    Load credentials from JSON file

    Expected format:
    [
        {"username": "admin", "password": "Pass123", "domain": "CORP"},
        {"username": "svc", "ntlm_hash": "aad3b435...", "domain": "CORP"}
    ]

    Args:
        filepath: Path to JSON credentials file

    Returns:
        List of Credential objects
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Credentials file not found: {filepath}")

    with open(path, 'r') as f:
        data = json.load(f)

    credentials = []
    for item in data:
        cred = Credential(
            username=item.get('username'),
            password=item.get('password'),
            ntlm_hash=item.get('ntlm_hash'),
            domain=item.get('domain', '.')
        )
        credentials.append(cred)

    return credentials


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if needed

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def validate_file_exists(filepath: str) -> bool:
    """
    Check if file exists

    Args:
        filepath: Path to check

    Returns:
        True if exists, False otherwise
    """
    return Path(filepath).exists()


def get_filename(filepath: str) -> str:
    """
    Extract filename from path

    Args:
        filepath: Full path to file

    Returns:
        Filename only
    """
    return Path(filepath).name