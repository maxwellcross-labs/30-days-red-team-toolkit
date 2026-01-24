"""
Validators
Input validation utilities
"""

import os
import re
from pathlib import Path
from typing import Tuple, List


class InputValidator:
    """Validate user inputs"""

    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        """
        Validate hostname or IP address

        Args:
            hostname: Hostname or IP to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hostname:
            return False, "Hostname cannot be empty"

        # Check for IP address
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, hostname):
            # Validate IP octets
            octets = hostname.split('.')
            for octet in octets:
                if int(octet) > 255:
                    return False, f"Invalid IP address: {hostname}"
            return True, ""

        # Check for hostname
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(hostname_pattern, hostname):
            return True, ""

        return False, f"Invalid hostname: {hostname}"

    @staticmethod
    def validate_port(port: int) -> Tuple[bool, str]:
        """
        Validate port number

        Args:
            port: Port number to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(port, int):
            try:
                port = int(port)
            except (ValueError, TypeError):
                return False, f"Port must be an integer: {port}"

        if port < 1 or port > 65535:
            return False, f"Port must be between 1 and 65535: {port}"

        if port < 1024:
            return True, f"Warning: Port {port} requires root privileges"

        return True, ""

    @staticmethod
    def validate_ssh_key(key_path: str) -> Tuple[bool, str]:
        """
        Validate SSH private key path

        Args:
            key_path: Path to SSH private key

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key_path:
            return False, "SSH key path cannot be empty"

        key_path_obj = Path(key_path)

        if not key_path_obj.exists():
            return False, f"SSH key not found: {key_path}"

        if not key_path_obj.is_file():
            return False, f"SSH key is not a file: {key_path}"

        # Check permissions (should be 600 or 400)
        try:
            mode = key_path_obj.stat().st_mode & 0o777

            if mode not in [0o600, 0o400]:
                return True, f"Warning: SSH key has insecure permissions: {oct(mode)}. Should be 600 or 400."

        except Exception:
            pass

        return True, ""

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate SSH username

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"

        # Basic username validation
        username_pattern = r'^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$'

        if re.match(username_pattern, username):
            return True, ""

        # More lenient check for domain usernames
        if '@' in username or '\\' in username:
            return True, ""

        return True, f"Warning: Unusual username format: {username}"

    @staticmethod
    def validate_tunnel_params(
            pivot_host: str,
            pivot_user: str,
            pivot_key: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate common tunnel parameters

        Args:
            pivot_host: Pivot hostname
            pivot_user: Pivot username
            pivot_key: SSH key path

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        warnings = []

        # Validate hostname
        is_valid, msg = InputValidator.validate_hostname(pivot_host)
        if not is_valid:
            errors.append(msg)

        # Validate username
        is_valid, msg = InputValidator.validate_username(pivot_user)
        if not is_valid:
            errors.append(msg)
        elif msg:
            warnings.append(msg)

        # Validate SSH key
        is_valid, msg = InputValidator.validate_ssh_key(pivot_key)
        if not is_valid:
            errors.append(msg)
        elif msg:
            warnings.append(msg)

        # Print warnings
        for warning in warnings:
            print(f"[!] {warning}")

        return len(errors) == 0, errors