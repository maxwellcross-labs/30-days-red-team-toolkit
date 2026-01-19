"""
Base Enumerator
===============

Abstract base class for all privilege escalation enumerators.
"""

from abc import ABC, abstractmethod
from typing import Optional
import subprocess

from .findings import FindingsCollection, Finding, FindingSeverity
from .config import Config


class BaseEnumerator(ABC):
    """
    Abstract base class for privilege escalation enumerators.

    Each enumerator is responsible for discovering a specific class
    of privilege escalation vectors.
    """

    # Override in subclasses
    name: str = "Base Enumerator"
    description: str = "Abstract base enumerator"

    def __init__(self, config: Config, findings: FindingsCollection):
        """
        Initialize the enumerator.

        Args:
            config: Framework configuration
            findings: Shared findings collection
        """
        self.config = config
        self.findings = findings

    @abstractmethod
    def enumerate(self) -> None:
        """
        Run enumeration and populate findings.

        Must be implemented by subclasses.
        """
        pass

    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message with appropriate formatting.

        Args:
            message: Message to log
            level: Log level (info, success, warning, error, critical)
        """
        if self.config.quiet and level in ('info',):
            return

        prefixes = {
            'info': '[*]',
            'success': '[+]',
            'warning': '[!]',
            'error': '[-]',
            'critical': '[!!!]'
        }

        prefix = prefixes.get(level, '[*]')
        print(f"{prefix} {message}")

    def run_command(
            self,
            command: str,
            timeout: Optional[int] = None,
            shell: bool = True
    ) -> Optional[str]:
        """
        Execute a shell command and return output.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            shell: Use shell execution

        Returns:
            Command stdout or None on failure
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout or self.config.timeout
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command[:50]}...", "warning")
            return None
        except Exception as e:
            if self.config.verbose:
                self.log(f"Command failed: {e}", "error")
            return None

    def add_finding(
            self,
            category: str,
            severity: FindingSeverity,
            finding: str,
            exploitation: str,
            impact: str,
            target: Optional[str] = None,
            **metadata
    ) -> Finding:
        """
        Add a finding to the collection.

        Convenience wrapper around findings.add_finding().
        """
        return self.findings.add_finding(
            category=category,
            severity=severity,
            finding=finding,
            exploitation=exploitation,
            impact=impact,
            target=target,
            **metadata
        )

    def print_header(self) -> None:
        """Print enumerator header"""
        print(f"\n{'=' * 60}")
        print(f"{self.name.upper()}")
        print(f"{'=' * 60}")