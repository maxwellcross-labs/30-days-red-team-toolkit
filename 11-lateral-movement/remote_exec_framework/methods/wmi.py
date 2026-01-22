"""
WMI Remote Execution using Impacket's wmiexec
Primary method for stealthy remote command execution
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseExecutionMethod
from ..core.models import ExecutionMethod, Credential


class WMIExecutionMethod(BaseExecutionMethod):
    """
    Remote execution via WMI using Impacket's wmiexec

    WMI (Windows Management Instrumentation) provides a powerful
    interface for remote management. wmiexec leverages this for
    command execution.

    Advantages:
        - No service installation required
        - Uses legitimate Windows management interface
        - Supports both password and hash authentication
        - Lower footprint than PSExec

    Disadvantages:
        - Requires WMI service running on target
        - Can be blocked by firewall
        - Creates process on target (shows in task list)

    Detection:
        - Event ID 4688 (Process Creation)
        - WMI activity logs
        - Network traffic on RPC ports
    """

    method = ExecutionMethod.WMI
    supports_hash = True
    supports_password = True

    def build_command(self, target: str, credential: Credential,
                      command: str) -> str:
        """
        Build wmiexec command

        Formats:
            Password: wmiexec.py domain/user:'password'@target 'command'
            Hash: wmiexec.py domain/user@target -hashes :hash 'command'
        """
        if credential.password:
            cmd = (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}:'{credential.password}'@{target} "
                f"'{command}'"
            )
        else:
            cmd = (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}@{target} "
                f"-hashes :{credential.ntlm_hash} "
                f"'{command}'"
            )

        return cmd

    def parse_output(self, output_text: str, stderr: str) -> Tuple[bool, Optional[str]]:
        """
        Parse wmiexec output

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
            ('error', 'Execution error'),
            ('connection refused', 'Connection refused'),
            ('timed out', 'Connection timed out'),
            ('status_logon_failure', 'Logon failure')
        ]

        for indicator, message in error_indicators:
            if indicator in combined:
                return False, message

        # If we got output without errors, success
        if output_text.strip():
            return True, None

        return False, "No output received"