"""
Command execution utilities for Remote Execution Framework
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

    def execute(self, command: str, timeout: Optional[int] = None) -> CommandResult:
        """
        Execute a shell command

        Args:
            command: Command string to execute
            timeout: Timeout in seconds (uses default if not specified)

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
            return CommandResult(
                stdout="",
                stderr="",
                returncode=-1,
                success=False,
                error=str(e)
            )

    def execute_interactive(self, command: str) -> bool:
        """
        Execute command interactively (no output capture)

        Args:
            command: Command to execute

        Returns:
            True if completed, False if error/interrupted
        """
        try:
            subprocess.run(command, shell=True)
            return True
        except KeyboardInterrupt:
            return False
        except Exception:
            return False


# Global executor instance
executor = CommandExecutor()