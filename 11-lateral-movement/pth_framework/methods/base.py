"""
Base authentication method class
Abstract base for all PTH authentication implementations
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import AuthResult, AuthMethod, AccessLevel, Credential
from ..utils.output import output
from ..utils.executor import executor


class BaseAuthMethod(ABC):
    """Abstract base class for authentication methods"""

    method: AuthMethod = None
    timeout: int = 30

    def __init__(self, timeout: int = 30):
        """
        Initialize authentication method

        Args:
            timeout: Command execution timeout in seconds
        """
        self.timeout = timeout

    @abstractmethod
    def build_command(self, target: str, credential: Credential,
                      command: Optional[str] = None) -> str:
        """
        Build the command string for this auth method

        Args:
            target: Target IP or hostname
            credential: Credential object with username, hash, domain
            command: Optional command to execute on target

        Returns:
            Command string to execute
        """
        pass

    @abstractmethod
    def parse_output(self, output_text: str) -> tuple:
        """
        Parse command output to determine success and access level

        Args:
            output_text: Combined stdout/stderr from command

        Returns:
            Tuple of (success: bool, access_level: AccessLevel, error_message: str)
        """
        pass

    def authenticate(self, target: str, credential: Credential,
                     command: Optional[str] = None) -> AuthResult:
        """
        Perform authentication attempt

        Args:
            target: Target IP or hostname
            credential: Credential object
            command: Optional command to execute

        Returns:
            AuthResult with attempt details
        """
        output.newline()
        output.info(f"Pass-the-Hash via {self.method.value}")
        output.target_header(target, credential.username, credential.domain)

        if credential.ntlm_hash:
            # Show truncated hash for security
            hash_preview = credential.ntlm_hash[:8] + "..." if len(credential.ntlm_hash) > 8 else credential.ntlm_hash
            output.info(f"Hash: {hash_preview}")

        # Build and display command
        cmd = self.build_command(target, credential, command)
        output.command_display(cmd)

        # Execute
        result = executor.execute(cmd, self.timeout)

        # Handle timeout
        if result.timeout:
            output.failure("Connection timeout")
            return AuthResult(
                target=target,
                username=credential.username,
                domain=credential.domain,
                method=self.method,
                success=False,
                error_message="Connection timeout"
            )

        # Handle execution error
        if result.error and not result.timeout:
            output.failure(f"Error: {result.error}")
            return AuthResult(
                target=target,
                username=credential.username,
                domain=credential.domain,
                method=self.method,
                success=False,
                error_message=result.error
            )

        # Display output
        output.output_display(result.output)

        # Parse results
        success, access_level, error_msg = self.parse_output(result.output)

        # Log result
        if success:
            if access_level == AccessLevel.ADMIN:
                output.success("SUCCESS! Administrator access achieved")
            else:
                output.info("Connected but not admin")
        else:
            output.failure("Authentication failed")

        return AuthResult(
            target=target,
            username=credential.username,
            domain=credential.domain,
            method=self.method,
            success=success,
            access_level=access_level,
            command=command,
            output=result.output if success else None,
            error_message=error_msg
        )