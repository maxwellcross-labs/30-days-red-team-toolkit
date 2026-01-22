"""
PowerShell Remoting (WinRM) Execution using evil-winrm
For interactive and non-interactive remote PowerShell sessions
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseExecutionMethod
from ..core.models import ExecutionMethod, Credential
from ..utils.output import output
from ..utils.executor import executor


class PSRemotingExecutionMethod(BaseExecutionMethod):
    """
    Remote execution via PowerShell Remoting (WinRM) using evil-winrm

    PowerShell Remoting uses the WinRM service for remote
    management. evil-winrm provides an excellent interface.

    Advantages:
        - Native Windows remote management
        - Full PowerShell capabilities
        - Interactive session support
        - Upload/download support

    Disadvantages:
        - Requires password (no hash support in standard mode)
        - WinRM must be enabled on target
        - Heavily logged in mature environments
        - Port 5985/5986 may be monitored

    Detection:
        - Event ID 4624 (Logon Type 3)
        - WinRM service logs
        - PowerShell script block logging
        - Event ID 400/403 (Engine Lifecycle)

    OPSEC Note:
        - PSRemoting is often more monitored than WMI
        - Script block logging captures all PowerShell commands
        - Consider disabling logging after initial access
    """

    method = ExecutionMethod.PSREMOTING
    supports_hash = False  # evil-winrm requires password for basic use
    supports_password = True

    def build_command(self, target: str, credential: Credential,
                      command: str) -> str:
        """
        Build evil-winrm command for single command execution

        Format: evil-winrm -i target -u user -p 'password' -c 'command'
        """
        cmd = (
            f"evil-winrm "
            f"-i {target} "
            f"-u {credential.username} "
            f"-p '{credential.password}' "
            f"-c '{command}'"
        )

        return cmd

    def parse_output(self, output_text: str, stderr: str) -> Tuple[bool, Optional[str]]:
        """
        Parse evil-winrm output

        Args:
            output_text: stdout from command
            stderr: stderr from command

        Returns:
            Tuple of (success, error_message)
        """
        combined = (output_text + stderr).lower()

        # Check for common errors
        if 'error' in combined and 'winrm' in combined:
            return False, "WinRM connection error"

        if 'access denied' in combined:
            return False, "Access denied"

        if 'authentication failed' in combined:
            return False, "Authentication failed"

        if 'connection refused' in combined:
            return False, "Connection refused - WinRM may not be enabled"

        # If we got output without obvious errors
        if output_text.strip():
            return True, None

        return False, "No output received"

    def interactive_session(self, target: str, credential: Credential) -> bool:
        """
        Start interactive PowerShell Remoting session

        This launches evil-winrm in interactive mode, giving
        the operator a full PowerShell session on the target.

        Args:
            target: Target IP or hostname
            credential: Credential object (must have password)

        Returns:
            True if session completed normally, False otherwise
        """
        # Validate password
        if not credential.password:
            output.failure("Interactive session requires password")
            return False

        output.newline()
        output.info("Starting interactive PSRemoting session...")
        output.info(f"Target: {target}")
        output.info(f"User: {credential}")

        cmd = (
            f"evil-winrm "
            f"-i {target} "
            f"-u {credential.username} "
            f"-p '{credential.password}'"
        )

        output.info(f"Command: {cmd}")
        output.newline()
        output.success("Launching interactive session...")
        output.warning("Type 'exit' to close session")

        return executor.execute_interactive(cmd)