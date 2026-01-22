"""
Base scanner class
Abstract base for all protocol scanners
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import Protocol, HostInfo, ScanResult
from ..utils.output import output
from ..utils.executor import executor


class BaseScanner(ABC):
    """Abstract base class for protocol scanners"""

    protocol: Protocol = None
    default_port: int = None
    timeout: int = 300

    def __init__(self, timeout: int = 300):
        """
        Initialize scanner

        Args:
            timeout: Scan timeout in seconds
        """
        self.timeout = timeout

    @abstractmethod
    def build_command(self, network: str) -> str:
        """
        Build the scan command for this protocol

        Args:
            network: Network range to scan

        Returns:
            Command string to execute
        """
        pass

    @abstractmethod
    def parse_output(self, output_text: str) -> List[HostInfo]:
        """
        Parse command output to extract hosts

        Args:
            output_text: Raw command output

        Returns:
            List of HostInfo objects
        """
        pass

    def scan(self, network: str) -> ScanResult:
        """
        Scan network for hosts with this protocol

        Args:
            network: Network range to scan (e.g., 192.168.1.0/24)

        Returns:
            ScanResult with discovered hosts
        """
        output.scan_header(self.protocol.value, network)

        # Build and execute command
        cmd = self.build_command(network)
        result = executor.execute(cmd, self.timeout)

        # Handle timeout
        if result.timeout:
            output.failure("Enumeration timeout")
            return ScanResult(
                protocol=self.protocol,
                network=network,
                error="Scan timed out",
                scan_duration=result.duration
            )

        # Handle errors
        if result.error:
            output.failure(f"Error: {result.error}")
            return ScanResult(
                protocol=self.protocol,
                network=network,
                error=result.error,
                scan_duration=result.duration
            )

        # Parse results
        hosts = self.parse_output(result.stdout)

        # Log found hosts
        for host in hosts:
            output.host_found(host.ip, self.protocol.value)

        output.scan_summary(self.protocol.value, len(hosts))

        return ScanResult(
            protocol=self.protocol,
            network=network,
            hosts_found=hosts,
            scan_duration=result.duration
        )