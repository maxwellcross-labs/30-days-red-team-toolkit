"""
Base execution method class
Abstract base for all remote execution implementations
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import ExecutionResult, ExecutionMethod, Credential
from utils.output import output
from utils.executor import executor


class BaseExecutionMethod(ABC):
    """Abstract base class for remote execution methods"""

    method: ExecutionMethod = None
    timeout: int = 30
    supports_hash: bool = True
    supports_password: bool = True

    def __init__(self, timeout: int = 30):
        """
        Initialize execution method

        Args:
            timeout: Command execution timeout in seconds
        """
        self.timeout = timeout

    @abstractmethod
    def build_command(self, target: str, credential: Credential,
                      command: str) -> str:
        """
        Build the command string for this execution method

        Args:
            target: Target IP or hostname
            credential: Credential object with auth info
            command: Command to execute on target

        Returns:
            Command string to execute
        """
        pass

    @abstractmethod
    def parse_output(self, output_text: str, stderr: str) -> tuple:
        """
        Parse command output to determine success

        Args:
            output_text: stdout from command
            stderr: stderr from command

        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        pass

    def validate_credential(self, credential: Credential) -> tuple:
        """
        Validate credential is compatible with this method

        Args:
            credential: Credential to validate

        Returns:
            Tuple of (valid: bool, error_message: str or None)
        """
        if credential.password and not self.supports_password:
            return False, f"{self.method.value} does not support password auth"

        if credential.ntlm_hash and not credential.password and not self.supports_hash:
            return False, f"{self.method.value} does not support hash auth"

        return True, None

    def execute(self, target: str, credential: Credential,
                command: str = "whoami") -> ExecutionResult:
        """
        Execute command on remote target

        Args:
            target: Target IP or hostname
            credential: Credential object
            command: Command to execute

        Returns:
            ExecutionResult with attempt details
        """
        # Validate credential
        valid, error = self.validate_credential(credential)
        if not valid:
            output.failure(error)
            return ExecutionResult(
                target=target,
                method=self.method,
                command=command,
                success=False,
                error=error
            )

        # Display header
        output.newline()
        output.execution_header(
            self.method.value,
            target,
            credential.username,
            credential.domain,
            command
        )

        # Build command
        cmd = self.build_command(target, credential, command)
        output.info("Executing...")

        # Execute
        result = executor.execute(cmd, self.timeout)

        # Handle timeout
        if result.timeout:
            output.failure(f"{self.method.value} timeout")
            return ExecutionResult(
                target=target,
                method=self.method,
                command=command,
                success=False,
                error="Execution timeout"
            )

        # Parse output
        success, error_msg = self.parse_output(result.stdout, result.stderr)

        # Log result
        if success:
            output.success("SUCCESS!")
            if result.stdout:
                output.output_display(result.stdout)
        else:
            output.failure("Execution failed")
            if error_msg:
                output.info(f"Error: {error_msg}")

        return ExecutionResult(
            target=target,
            method=self.method,
            command=command,
            success=success,
            output=result.stdout if success else None,
            error=error_msg
        )
