"""
Report generation for Remote Execution Framework
Generates JSON reports and console summaries
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import ExecutionResult, MultiTargetResult
from ..utils.output import output
from ..utils.files import ensure_directory


class ReportGenerator:
    """Generate reports from remote execution operations"""

    def __init__(self, output_dir: str = "remote_exec"):
        """
        Initialize report generator

        Args:
            output_dir: Directory for report files
        """
        self.output_dir = ensure_directory(output_dir)
        self.execution_results: List[ExecutionResult] = []

    def add_result(self, result: ExecutionResult):
        """
        Add execution result to report

        Args:
            result: ExecutionResult from execution attempt
        """
        self.execution_results.append(result)

    def get_successful(self) -> List[ExecutionResult]:
        """Get all successful execution results"""
        return [r for r in self.execution_results if r.success]

    def get_failed(self) -> List[ExecutionResult]:
        """Get all failed execution results"""
        return [r for r in self.execution_results if not r.success]

    def print_summary(self):
        """Print summary to console"""
        output.banner("REMOTE EXECUTION REPORT")

        successful = self.get_successful()
        failed = self.get_failed()

        output.success(f"Successful executions: {len(successful)}")
        output.failure(f"Failed executions: {len(failed)}")

        if successful:
            output.newline()
            output.success("Successful targets:")
            for result in successful:
                print(f"    {result.target} ({result.method.value})")

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
            filename = f"exec_report_{timestamp}.json"

        report_path = self.output_dir / filename

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'successful': len(self.get_successful()),
                'failed': len(self.get_failed()),
                'total': len(self.execution_results)
            },
            'results': [r.to_dict() for r in self.execution_results]
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        output.success(f"Report saved to: {report_path}")

        return report_path

    def print_multi_target_summary(self, results: MultiTargetResult):
        """
        Print multi-target execution summary

        Args:
            results: MultiTargetResult from multi-target operation
        """
        output.banner("EXECUTION SUMMARY")

        output.success(f"Successful: {len(results.successful)}")
        output.failure(f"Failed: {len(results.failed)}")

        if results.successful:
            output.newline()
            output.success("Successful targets:")
            for item in results.successful:
                target = item.get('target', 'unknown')
                print(f"    {target}")