"""
Network utilities for Target Enumeration Framework
IP validation, parsing, and network operations
"""

import socket
import re
from typing import Optional, List


def is_valid_ip(ip: str) -> bool:
    """
    Validate IP address format

    Args:
        ip: String to validate

    Returns:
        True if valid IPv4 address
    """
    try:
        socket.inet_aton(ip)
        return True
    except (socket.error, OSError):
        return False


def extract_ips_from_text(text: str) -> List[str]:
    """
    Extract all valid IP addresses from text

    Args:
        text: Text to search

    Returns:
        List of valid IP addresses found
    """
    # Regex pattern for IPv4 addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    potential_ips = re.findall(ip_pattern, text)

    # Validate each potential IP
    valid_ips = []
    for ip in potential_ips:
        if is_valid_ip(ip):
            # Additional validation - each octet should be 0-255
            octets = ip.split('.')
            if all(0 <= int(octet) <= 255 for octet in octets):
                valid_ips.append(ip)

    return valid_ips


def parse_network_range(network: str) -> Optional[str]:
    """
    Parse and validate network range notation

    Args:
        network: Network in CIDR notation (e.g., 192.168.1.0/24)

    Returns:
        Validated network string or None if invalid
    """
    if '/' in network:
        ip_part, cidr = network.split('/', 1)

        if not is_valid_ip(ip_part):
            return None

        try:
            cidr_int = int(cidr)
            if not 0 <= cidr_int <= 32:
                return None
        except ValueError:
            return None

        return network

    # Single IP
    if is_valid_ip(network):
        return network

    # IP range (e.g., 192.168.1.1-254)
    if '-' in network:
        return network

    return None


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address

    Args:
        hostname: Hostname to resolve

    Returns:
        IP address or None if resolution fails
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def reverse_lookup(ip: str) -> Optional[str]:
    """
    Perform reverse DNS lookup

    Args:
        ip: IP address to lookup

    Returns:
        Hostname or None if lookup fails
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return None