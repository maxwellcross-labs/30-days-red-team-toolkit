"""
Report generation for Automated Lateral Movement Framework
Generates JSON reports and console summaries
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import (
    AccessMatrix,
    MovementChain,
    BeaconDeployment
)
from ..utils.output import output
from ..utils.files import ensure_directory, save_json


class ReportGenerator:
    """Generate comprehensive lateral movement reports"""

    def __init__(self, output_dir: str = "automated_lm"):
        """
        Initialize report generator

        Args:
            output_dir: Directory for report files
        """
        self.output_dir = ensure_directory(output_dir)
        self.access_matrix: Optional[AccessMatrix] = None
        self.movement_chain: Optional[MovementChain] = None
        self.beacon_deployments: List[BeaconDeployment] = []

    def set_access_matrix(self, matrix: AccessMatrix):
        """Set access matrix for reporting"""
        self.access_matrix = matrix

    def set_movement_chain(self, chain: MovementChain):
        """Set movement chain for reporting"""
        self.movement_chain = chain

    def add_beacon_deployments(self, deployments: List[BeaconDeployment]):
        """Add beacon deployment results"""
        self.beacon_deployments.extend(deployments)

    def save_access_matrix(self, filename: str = "access_matrix.json") -> Path:
        """
        Save access matrix to JSON file

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        if not self.access_matrix:
            return None

        filepath = self.output_dir / filename
        save_json(self.access_matrix.to_dict(), filepath)
        output.success(f"Access matrix saved to: {filepath}")
        return filepath

    def save_movement_chain(self, filename: str = "movement_chain.json") -> Path:
        """
        Save movement chain to JSON file

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        if not self.movement_chain:
            return None

        filepath = self.output_dir / filename
        save_json(self.movement_chain.to_dict(), filepath)
        output.success(f"Movement chain saved to: {filepath}")
        return filepath

    def save_full_report(self, filename: str = None) -> Path:
        """
        Save comprehensive report to JSON file

        Args:
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lm_report_{timestamp}.json"

        filepath = self.output_dir / filename

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._build_summary(),
            'access_matrix': self.access_matrix.to_dict() if self.access_matrix else None,
            'movement_chain': self.movement_chain.to_dict() if self.movement_chain else None,
            'beacon_deployments': [d.to_dict() for d in self.beacon_deployments]
        }

        save_json(report_data, filepath)
        output.success(f"Full report saved to: {filepath}")
        return filepath

    def _build_summary(self) -> dict:
        """Build summary statistics"""
        summary = {}

        if self.access_matrix:
            summary['access'] = {
                'total_entries': len(self.access_matrix.entries),
                'admin_access': len(self.access_matrix.get_admin_access()),
                'user_access': len(self.access_matrix.get_user_access()),
                'unique_targets': len(self.access_matrix.get_targets_with_admin())
            }

        if self.movement_chain:
            summary['movement'] = {
                'total_steps': len(self.movement_chain.steps),
                'successful_steps': len(self.movement_chain.get_successful_steps()),
                'compromised_hosts': len(self.movement_chain.compromised_hosts)
            }

        if self.beacon_deployments:
            successful = sum(1 for d in self.beacon_deployments if d.success)
            summary['beacons'] = {
                'total_deployments': len(self.beacon_deployments),
                'successful': successful,
                'failed': len(self.beacon_deployments) - successful
            }

        return summary

    def print_summary(self):
        """Print comprehensive summary to console"""
        output.banner("LATERAL MOVEMENT REPORT")

        # Compromised hosts
        if self.movement_chain:
            output.success(f"Compromised hosts: {len(self.movement_chain.compromised_hosts)}")

            if self.movement_chain.compromised_hosts:
                output.newline()
                output.info("Compromised systems:")
                for host in self.movement_chain.compromised_hosts:
                    print(f"    {host}")

        # Movement chain visualization
        if self.movement_chain and self.movement_chain.steps:
            output.newline()
            output.info("Lateral Movement Chain:")
            for i, step in enumerate(self.movement_chain.get_successful_steps(), 1):
                output.chain_step(
                    i,
                    step.credential.domain,
                    step.credential.username,
                    step.target
                )

        # Beacon summary
        if self.beacon_deployments:
            successful = sum(1 for d in self.beacon_deployments if d.success)
            output.newline()
            output.success(f"Beacons deployed: {successful}/{len(self.beacon_deployments)}")