"""
File utilities for Target Enumeration Framework
Handles file operations and output generation
"""

import json
from pathlib import Path
from typing import List


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


def write_ip_list(filepath: str, ips: List[str]) -> Path:
    """
    Write list of IPs to file (one per line)

    Args:
        filepath: Output file path
        ips: List of IP addresses

    Returns:
        Path to created file
    """
    path = Path(filepath)

    with open(path, 'w') as f:
        for ip in ips:
            f.write(f"{ip}\n")

    return path


def write_json_report(filepath: str, data: dict) -> Path:
    """
    Write data to JSON file

    Args:
        filepath: Output file path
        data: Dictionary to serialize

    Returns:
        Path to created file
    """
    path = Path(filepath)

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

    return path


def load_targets_from_file(filepath: str) -> List[str]:
    """
    Load target IPs from file

    Args:
        filepath: Path to file with one target per line

    Returns:
        List of targets
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]