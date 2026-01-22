"""
Core Target Enumeration Framework
Main orchestrator for lateral movement target discovery
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    TargetCollection,
    FrameworkConfig,
    Protocol
)
from analyzer import HighValueAnalyzer
from scanners import get_scanner, get_all_scanners, list_protocols
from reports import ReportGenerator
from utils.output import output
from utils.files import ensure_directory
from utils.network import parse_network_range


class TargetEnumerationFramework:
    """
    Main Target Enumeration Framework

    Discovers and categorizes potential lateral movement targets
    across a network using multiple protocol scanners.

    Usage:
        framework = TargetEnumerationFramework()

        # Full auto enumeration
        collection = framework.auto_enumerate("192.168.1.0/24")

        # Single protocol scan
        collection = framework.scan_protocol("192.168.1.0/24", "smb")

        # Custom protocol selection
        collection = framework.scan_protocols(
            "192.168.1.0/24",
            protocols=["smb", "winrm", "rdp"]
        )

        # Generate reports
        framework.generate_reports()
    """

    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize framework

        Args:
            config: Optional configuration object
        """
        self.config = config or FrameworkConfig()
        self.output_dir = ensure_directory(self.config.output_dir)
        self.collection = TargetCollection()
        self.analyzer = HighValueAnalyzer()
        self.report_gen = ReportGenerator(str(self.output_dir))
        self.scanned_network = None

        output.success("Lateral Movement Target Enumerator initialized")
        output.success(f"Output directory: {self.output_dir}")

    def scan_protocol(self, network: str, protocol: str) -> TargetCollection:
        """
        Scan network for single protocol

        Args:
            network: Network range (e.g., 192.168.1.0/24)
            protocol: Protocol to scan ('smb', 'winrm', 'rdp', 'ssh')

        Returns:
            TargetCollection with discovered hosts
        """
        # Validate network
        validated = parse_network_range(network)
        if not validated:
            output.failure(f"Invalid network range: {network}")
            return self.collection

        self.scanned_network = network

        # Get scanner and run
        scanner = get_scanner(protocol, timeout=self.config.timeout)
        result = scanner.scan(network)

        # Add discovered hosts to collection
        for host in result.hosts_found:
            self.collection.add_host(host)

        return self.collection

    def scan_protocols(self, network: str,
                       protocols: List[str] = None) -> TargetCollection:
        """
        Scan network for multiple protocols

        Args:
            network: Network range
            protocols: List of protocols (default: all)

        Returns:
            TargetCollection with discovered hosts
        """
        protocols = protocols or list_protocols()

        for protocol in protocols:
            self.scan_protocol(network, protocol)

        return self.collection

    def auto_enumerate(self, network: str) -> TargetCollection:
        """
        Automated full target enumeration

        Scans all protocols and identifies high-value targets.

        Args:
            network: Network range to enumerate

        Returns:
            TargetCollection with all discovered and categorized hosts
        """
        output.banner("LATERAL MOVEMENT TARGET ENUMERATION")
        output.info(f"Network: {network}")

        # Validate network
        validated = parse_network_range(network)
        if not validated:
            output.failure(f"Invalid network range: {network}")
            return self.collection

        self.scanned_network = network

        # Scan all protocols
        scanners = get_all_scanners(timeout=self.config.timeout)

        for scanner in scanners:
            result = scanner.scan(network)

            # Add hosts to collection
            for host in result.hosts_found:
                self.collection.add_host(host)

        # Analyze for high-value targets
        self.analyzer.analyze_collection(self.collection)

        # Generate reports
        self.generate_reports()

        # Print summary
        self.report_gen.print_summary(self.collection)

        return self.collection

    def identify_high_value(self) -> int:
        """
        Analyze collected hosts for high-value targets

        Returns:
            Number of high-value targets identified
        """
        return self.analyzer.analyze_collection(self.collection)

    def generate_reports(self) -> dict:
        """
        Generate all reports and target lists

        Returns:
            Dictionary of generated file paths
        """
        output.newline()

        # Generate target list files
        files = self.report_gen.generate_target_lists(self.collection)

        # Generate JSON report
        self.report_gen.generate_json_report(
            self.collection,
            self.scanned_network
        )

        return files

    def get_targets(self, category: str = 'all') -> List[str]:
        """
        Get list of target IPs by category

        Args:
            category: 'windows', 'linux', 'high_value', 'domain_controllers', 'all'

        Returns:
            List of IP addresses
        """
        return self.collection.get_ips_by_category(category)

    @staticmethod
    def available_protocols() -> List[str]:
        """Get list of available scan protocols"""
        return list_protocols()