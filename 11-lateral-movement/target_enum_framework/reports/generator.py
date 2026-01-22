"""
Report generation for Target Enumeration Framework
Generates target lists and JSON reports
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import TargetCollection, ScanResult
from ..utils.output import output
from ..utils.files import ensure_directory, write_ip_list, write_json_report


class ReportGenerator:
    """Generate reports and target lists from enumeration results"""

    def __init__(self, output_dir: str = "lm_targets"):
        """
        Initialize report generator

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = ensure_directory(output_dir)

    def generate_target_lists(self, collection: TargetCollection) -> dict:
        """
        Generate formatted target lists for tools

        Creates separate files for:
            - Windows targets
            - Linux targets
            - High-value targets
            - Domain controllers
            - All targets

        Args:
            collection: TargetCollection with enumerated hosts

        Returns:
            Dictionary of generated file paths
        """
        output.info("Generating target lists...")

        files_created = {}

        # Windows targets
        windows_ips = list(collection.windows_hosts.keys())
        if windows_ips:
            path = write_ip_list(
                self.output_dir / "windows_targets.txt",
                windows_ips
            )
            files_created['windows'] = str(path)
            output.success(f"Windows targets: {path}")

        # Linux targets
        linux_ips = list(collection.linux_hosts.keys())
        if linux_ips:
            path = write_ip_list(
                self.output_dir / "linux_targets.txt",
                linux_ips
            )
            files_created['linux'] = str(path)
            output.success(f"Linux targets: {path}")

        # High-value targets
        hv_ips = list(collection.high_value.keys())
        if hv_ips:
            path = write_ip_list(
                self.output_dir / "high_value_targets.txt",
                hv_ips
            )
            files_created['high_value'] = str(path)
            output.success(f"High-value targets: {path}")

        # Domain controllers
        dc_ips = list(collection.domain_controllers.keys())
        if dc_ips:
            path = write_ip_list(
                self.output_dir / "domain_controllers.txt",
                dc_ips
            )
            files_created['domain_controllers'] = str(path)
            output.success(f"Domain controllers: {path}")

        # All targets
        all_ips = list(collection.all_hosts.keys())
        if all_ips:
            path = write_ip_list(
                self.output_dir / "all_targets.txt",
                all_ips
            )
            files_created['all'] = str(path)
            output.success(f"All targets: {path}")

        return files_created

    def generate_json_report(self, collection: TargetCollection,
                             network: str = None) -> Path:
        """
        Generate comprehensive JSON report

        Args:
            collection: TargetCollection with enumerated hosts
            network: Network range that was scanned

        Returns:
            Path to generated report
        """
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'network': network,
            'summary': {
                'total_hosts': len(collection.all_hosts),
                'windows_hosts': len(collection.windows_hosts),
                'linux_hosts': len(collection.linux_hosts),
                'domain_controllers': len(collection.domain_controllers),
                'high_value_targets': len(collection.high_value)
            },
            'targets': collection.to_dict()
        }

        report_path = self.output_dir / "targets_report.json"
        write_json_report(report_path, report_data)

        output.success(f"Full report: {report_path}")

        return report_path

    def print_summary(self, collection: TargetCollection):
        """
        Print enumeration summary to console

        Args:
            collection: TargetCollection with results
        """
        output.banner("ENUMERATION SUMMARY")

        output.success(f"Total hosts: {len(collection.all_hosts)}")
        output.success(f"Windows hosts: {len(collection.windows_hosts)}")
        output.success(f"Linux hosts: {len(collection.linux_hosts)}")
        output.success(f"Domain controllers: {len(collection.domain_controllers)}")
        output.success(f"High-value targets: {len(collection.high_value)}")