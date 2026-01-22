"""
Report generation for Pass-the-Hash Framework
Generates JSON reports and console summaries
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import AuthResult, AccessLevel, SprayResult
from ..utils.output import output
from ..utils.files import ensure_directory


class ReportGenerator:
    """Generate reports from PTH operations"""

    def __init__(self, output_dir: str = "pth_results"):
        """
        Initialize report generator

        Args:
            output_dir: Directory for report files
        """
        self.output_dir = ensure_directory(output_dir)
        self.successful_auths: List[AuthResult] = []
        self.failed_auths: List[AuthResult] = []

    def add_result(self, result: AuthResult):
        """
        Add authentication result to report

        Args:
            result: AuthResult from authentication attempt
        """
        if result.success:
            self.successful_auths.append(result)
        else:
            self.failed_auths.append(result)

    def get_admin_access(self) -> List[AuthResult]:
        """Get all results with admin access"""
        return [
            auth for auth in self.successful_auths
            if auth.access_level == AccessLevel.ADMIN
        ]

    def print_summary(self):
        """Print summary to console"""
        output.banner("PASS-THE-HASH REPORT")

        output.success(f"Successful authentications: {len(self.successful_auths)}")
        output.failure(f"Failed authentications: {len(self.failed_auths)}")

        admin_targets = self.get_admin_access()

        if admin_targets:
            output.newline()
            output.success(f"Admin access achieved on {len(admin_targets)} systems:")

            for auth in admin_targets:
                print(f"    {auth.target} - {auth.domain}\\{auth.username}")

    def save_json(self, filename: str = None) -> Path:
        """
        Save report to JSON file

        Args:
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pth_report_{timestamp}.json"

        report_path = self.output_dir / filename

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'successful': len(self.successful_auths),
                'failed': len(self.failed_auths),
                'admin_access': len(self.get_admin_access())
            },
            'successful': [auth.to_dict() for auth in self.successful_auths],
            'failed': [auth.to_dict() for auth in self.failed_auths]
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        output.success(f"Report saved to: {report_path}")

        return report_path

    def print_spray_results(self, results: SprayResult):
        """
        Print spray operation results

        Args:
            results: SprayResult from spray operation
        """
        output.banner("SPRAY RESULTS")

        output.success(f"Successful authentications: {len(results.successful)}")
        output.success(f"Admin access achieved: {len(results.admin_access)}")
        output.failure(f"Failed authentications: {len(results.failed)}")

        if results.admin_access:
            output.newline()
            output.success("Systems with admin access:")
            for target in results.admin_access:
                print(f"    {target}")


class SprayReporter:
    """Specialized reporter for spray operations"""

    def __init__(self, output_dir: str = "pth_results"):
        self.output_dir = ensure_directory(output_dir)
        self.report_gen = ReportGenerator(output_dir)

    def create_spray_result(self) -> SprayResult:
        """Create SprayResult from accumulated results"""
        result = SprayResult()

        for auth in self.report_gen.successful_auths:
            result.successful.append(auth.target)
            if auth.access_level == AccessLevel.ADMIN:
                result.admin_access.append(auth.target)

        for auth in self.report_gen.failed_auths:
            result.failed.append(auth.target)

        result.total_targets = len(result.successful) + len(result.failed)

        return result

    def add_result(self, result: AuthResult):
        """Add result to reporter"""
        self.report_gen.add_result(result)

    def finalize(self) -> SprayResult:
        """Generate final spray results and report"""
        spray_result = self.create_spray_result()
        self.report_gen.print_spray_results(spray_result)
        self.report_gen.save_json()
        return spray_result