"""
Command execution utilities for Automated Lateral Movement Framework
Handles subprocess execution with timeouts and error handling
"""

import subprocess
from typing import Optional
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of command execution"""
    stdout: str
    stderr: str
    returncode: int
    success: bool
    timeout: bool = False
    error: Optional[str] = None

    @property
    def output(self) -> str:
        """Combined stdout and stderr"""
        return self.stdout + self.stderr


class CommandExecutor:
    """Execute shell commands with proper error handling"""

    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout

    def execute(self, command: str, timeout: Optional[int] = None,
                suppress_errors: bool = False) -> CommandResult:
        """
        Execute a shell command

        Args:
            command: Command string to execute
            timeout: Timeout in seconds (uses default if not specified)
            suppress_errors: If True, don't raise exceptions

        Returns:
            CommandResult with execution details
        """
        timeout = timeout or self.default_timeout

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                success=result.returncode == 0
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                stdout="",
                stderr="",
                returncode=-1,
                success=False,
                timeout=True,
                error="Command timed out"
            )

        except Exception as e:
            if suppress_errors:
                return CommandResult(
                    stdout="",
                    stderr="",
                    returncode=-1,
                    success=False,
                    error=str(e)
                )
            raise

    def execute_silent(self, command: str, timeout: Optional[int] = None) -> CommandResult:
        """
        Execute command silently, suppressing all errors

        Args:
            command: Command to execute
            timeout: Optional timeout override

        Returns:
            CommandResult (may indicate failure but won't raise)
        """
        return self.execute(command, timeout, suppress_errors=True)


# Global executor instance
executor = CommandExecutor()