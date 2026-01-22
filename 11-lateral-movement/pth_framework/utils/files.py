"""
File utilities for Pass-the-Hash Framework
Handles loading targets, credentials, and configuration files
"""

import sys
from pathlib import Path
from typing import List, Optional
import json

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
        {"username": "admin", "ntlm_hash": "...", "domain": "CORP"},
        ...
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
            ntlm_hash=item.get('ntlm_hash'),
            domain=item.get('domain', '.')
        )
        credentials.append(cred)

    return credentials


def parse_hash_line(line: str, default_domain: str = ".") -> Optional[Credential]:
    """
    Parse credential from common formats

    Supported formats:
        - username:ntlm_hash
        - domain\\username:ntlm_hash
        - domain/username:ntlm_hash

    Args:
        line: Line containing credential info
        default_domain: Domain to use if not specified

    Returns:
        Credential object or None if parsing fails
    """
    line = line.strip()
    if not line or ':' not in line:
        return None

    try:
        # Split on last colon (hash might contain colons in LM:NT format)
        parts = line.rsplit(':', 1)
        user_part = parts[0]
        hash_part = parts[1]

        # Check for domain separator
        domain = default_domain
        username = user_part

        if '\\' in user_part:
            domain, username = user_part.split('\\', 1)
        elif '/' in user_part:
            domain, username = user_part.split('/', 1)

        # Handle LM:NT format - take only NT hash
        if ':' in hash_part:
            hash_part = hash_part.split(':')[-1]

        return Credential(
            username=username,
            ntlm_hash=hash_part,
            domain=domain
        )

    except Exception:
        return None


def load_hashes_file(filepath: str, default_domain: str = ".") -> List[Credential]:
    """
    Load credentials from various hash file formats

    Args:
        filepath: Path to hash file
        default_domain: Default domain if not in file

    Returns:
        List of Credential objects
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Hash file not found: {filepath}")

    credentials = []

    with open(path, 'r') as f:
        for line in f:
            cred = parse_hash_line(line, default_domain)
            if cred:
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