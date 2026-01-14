import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Generate exploitation reports."""

    def __init__(self, output_dir: str = "task_exploits"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for storing reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_json_report(self, findings: Dict,
                             filename: str = None) -> str:
        """
        Generate a JSON report.

        Args:
            findings: Dictionary of findings
            filename: Optional filename

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"task_report_{timestamp}.json"

        filepath = self.output_dir / filename

        report = {
            'report_type': 'Scheduled Task Exploitation Assessment',
            'generated': datetime.now().isoformat(),
            'findings': findings,
            'summary': self._generate_summary(findings)
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        return str(filepath)

    def generate_text_report(self, findings: Dict,
                             filename: str = None) -> str:
        """
        Generate a text report.

        Args:
            findings: Dictionary of findings
            filename: Optional filename

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"task_report_{timestamp}.txt"

        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("SCHEDULED TASK EXPLOITATION ASSESSMENT REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # Summary
            summary = self._generate_summary(findings)
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Findings: {summary['total']}\n")
            f.write(f"  High Priority: {summary['high']}\n")
            f.write(f"  Medium Priority: {summary['medium']}\n")
            f.write(f"  Low Priority: {summary['low']}\n\n")

            # High priority findings
            if findings.get('high'):
                f.write("HIGH PRIORITY FINDINGS\n")
                f.write("-" * 70 + "\n")

                for i, finding in enumerate(findings['high'], 1):
                    f.write(f"\n[{i}] {finding.get('type', 'Unknown').upper()}\n")
                    f.write(f"    Task Name: {finding.get('task_name', 'N/A')}\n")
                    f.write(f"    Target: {finding.get('target_path', 'N/A')}\n")
                    f.write(f"    Running As: {finding.get('task_user', 'N/A')}\n")
                    f.write(f"    Next Run: {finding.get('next_run', 'N/A')}\n")
                    f.write(f"    Exploitation: {finding.get('exploitation', 'N/A')}\n")
                    f.write(f"    Impact: Execute code as {finding.get('task_user', 'privileged user')}\n")

            # Medium priority findings
            if findings.get('medium'):
                f.write("\n\nMEDIUM PRIORITY FINDINGS\n")
                f.write("-" * 70 + "\n")

                for i, finding in enumerate(findings['medium'], 1):
                    f.write(f"\n[{i}] {finding.get('type', 'Unknown').upper()}\n")
                    f.write(f"    Task Name: {finding.get('task_name', 'N/A')}\n")
                    f.write(f"    Target: {finding.get('target_path', 'N/A')}\n")
                    f.write(f"    Running As: {finding.get('task_user', 'N/A')}\n")
                    f.write(f"    Exploitation: {finding.get('exploitation', 'N/A')}\n")

            # Low priority findings
            if findings.get('low'):
                f.write("\n\nLOW PRIORITY FINDINGS\n")
                f.write("-" * 70 + "\n")

                for i, finding in enumerate(findings['low'], 1):
                    f.write(f"\n[{i}] {finding.get('type', 'Unknown').upper()}\n")
                    f.write(f"    Task Name: {finding.get('task_name', 'N/A')}\n")
                    f.write(f"    Target: {finding.get('target_path', 'N/A')}\n")

            # Recommendations
            f.write("\n\nRECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            f.write(self._generate_recommendations(findings))

            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")

        return str(filepath)

    def _generate_summary(self, findings: Dict) -> Dict:
        """Generate summary statistics."""
        return {
            'high': len(findings.get('high', [])),
            'medium': len(findings.get('medium', [])),
            'low': len(findings.get('low', [])),
            'info': len(findings.get('info', [])),
            'total': sum(len(findings.get(k, [])) for k in ['high', 'medium', 'low', 'info'])
        }

    def _generate_recommendations(self, findings: Dict) -> str:
        """Generate security recommendations based on findings."""
        recommendations = []

        if findings.get('high'):
            recommendations.append(
                "1. CRITICAL: Review and fix writable scheduled task scripts.\n"
                "   - Ensure scripts are stored in protected directories\n"
                "   - Remove write permissions for non-privileged users\n"
                "   - Consider using signed scripts with execution policies"
            )

        if findings.get('medium'):
            recommendations.append(
                "\n2. IMPORTANT: Secure executable directories for scheduled tasks.\n"
                "   - Move executables to protected locations (e.g., C:\\Windows\\System32)\n"
                "   - Remove unnecessary write permissions\n"
                "   - Implement application whitelisting"
            )

        if findings.get('low'):
            recommendations.append(
                "\n3. RECOMMENDED: Review PATH environment variable security.\n"
                "   - Ensure system directories appear before user-writable paths\n"
                "   - Remove unnecessary directories from PATH\n"
                "   - Monitor for DLL planting attempts"
            )

        if not recommendations:
            return "No critical recommendations at this time."

        return "\n".join(recommendations)


if __name__ == "__main__":
    # Example usage
    generator = ReportGenerator()

    sample_findings = {
        'high': [
            {
                'type': 'writable_script',
                'task_name': 'BackupTask',
                'target_path': 'C:\\Scripts\\backup.bat',
                'task_user': 'SYSTEM',
                'next_run': '2024-01-15 02:00:00',
                'exploitation': 'Modify script to inject payload'
            }
        ],
        'medium': [],
        'low': []
    }

    json_path = generator.generate_json_report(sample_findings)
    text_path = generator.generate_text_report(sample_findings)

    print(f"JSON report: {json_path}")
    print(f"Text report: {text_path}")