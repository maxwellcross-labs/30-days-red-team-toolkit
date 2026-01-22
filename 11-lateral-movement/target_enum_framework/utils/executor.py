"""
Command execution utilities for Target Enumeration Framework
Handles subprocess execution with timeouts and error handling
"""

import subprocess
import time
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
    duration: float = 0.0

    @property
    def output(self) -> str:
        """Combined stdout and stderr"""
        return self.stdout + self.stderr


class CommandExecutor:
    """Execute shell commands with proper error handling"""

    def __init__(self, default_timeout: int = 300):
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
        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time

            return CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                success=result.returncode == 0,
                duration=duration
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return CommandResult(
                stdout="",
                stderr="",
                returncode=-1,
                success=False,
                timeout=True,
                error="Command timed out",
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return CommandResult(
                stdout="",
                stderr="",
                returncode=-1,
                success=False,
                error=str(e),
                duration=duration
            )


# Global executor instance
executor = CommandExecutor()