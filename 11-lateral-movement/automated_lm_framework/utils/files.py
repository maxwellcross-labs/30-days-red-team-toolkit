"""
File utilities for Automated Lateral Movement Framework
Handles loading credentials, targets, and file operations
"""

import sys
import json
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..core.models import Credential, CredentialType
from output import output


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

    output.info(f"Loading targets from {filepath}...")

    with open(path, 'r') as f:
        targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    output.success(f"Loaded {len(targets)} targets")

    return targets


def load_credentials_from_file(filepath: str) -> List[Credential]:
    """
    Load credentials from file

    Supported formats:
        - username:domain:secret (hash if 32 chars or contains ':', else password)
        - JSON array of credential objects

    Args:
        filepath: Path to credentials file

    Returns:
        List of Credential objects
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Credentials file not found: {filepath}")

    output.info(f"Loading credentials from {filepath}...")

    # Try JSON first
    if filepath.endswith('.json'):
        return _load_json_credentials(path)

    # Otherwise parse as text
    return _load_text_credentials(path)


def _load_json_credentials(path: Path) -> List[Credential]:
    """Load credentials from JSON file"""
    with open(path, 'r') as f:
        data = json.load(f)

    credentials = []
    for item in data:
        cred = Credential(
            username=item.get('username'),
            domain=item.get('domain', '.'),
            password=item.get('password'),
            ntlm_hash=item.get('ntlm_hash') or item.get('hash')
        )
        credentials.append(cred)

    output.success(f"Loaded {len(credentials)} credentials")
    return credentials


def _load_text_credentials(path: Path) -> List[Credential]:
    """
    Load credentials from text file

    Format: username:domain:secret
    Secret is hash if 32 chars or contains ':', otherwise password
    """
    credentials = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ':' not in line:
                continue

            parts = line.split(':')

            if len(parts) < 3:
                continue

            username = parts[0]
            domain = parts[1] if parts[1] else '.'
            secret = ':'.join(parts[2:])  # Rejoin in case hash had colons

            # Determine if hash or password
            # NTLM hash is 32 hex chars, or might be LM:NT format
            is_hash = (
                              len(secret) == 32 and all(c in '0123456789abcdefABCDEF' for c in secret)
                      ) or (
                              ':' in secret and len(secret) >= 65  # LM:NT format
                      )

            if is_hash:
                # Extract NT hash if LM:NT format
                if ':' in secret:
                    secret = secret.split(':')[-1]
                cred = Credential(username=username, domain=domain, ntlm_hash=secret)
            else:
                cred = Credential(username=username, domain=domain, password=secret)

            credentials.append(cred)

    output.success(f"Loaded {len(credentials)} credentials")
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
    """Check if file exists"""
    return Path(filepath).exists()


def get_filename(filepath: str) -> str:
    """Extract filename from path"""
    return Path(filepath).name


def save_json(data: dict, filepath: Path) -> None:
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)