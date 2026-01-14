"""
Report Generator Module
Generates detailed UAC bypass assessment reports.
"""

import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime

import sys

sys.path.append(str(Path(__file__).parent.parent))

from ..core.detector import SystemDetector
from ..core.uac_checker import UACChecker
from ..utils.selector import BypassSelector


class ReportGenerator:
    """Generate UAC bypass assessment reports."""

    def __init__(self, output_dir: str = "uac_bypasses"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for storing reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.detector = SystemDetector()
        self.checker = UACChecker()
        self.selector = BypassSelector(output_dir)

    def generate_json_report(self, filename: str = None) -> str:
        """
        Generate a JSON assessment report.

        Args:
            filename: Optional filename

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"uac_report_{timestamp}.json"

        filepath = self.output_dir / filename

        report = {
            'report_type': 'UAC Bypass Assessment',
            'generated': datetime.now().isoformat(),
            'system_info': self.detector.get_full_info(),
            'uac_status': self.checker.get_status(),
            'compatible_methods': []
        }

        for method in self.selector.get_compatible_methods():
            report['compatible_methods'].append({
                'name': method['name'],
                'description': method['description'],
                'detection_risk': method['detection_risk'],
                'success_rate': method['success_rate']
            })

        # Add recommendation
        best = self.selector.select_best_method()
        report['recommended_method'] = best

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[+] Report saved: {filepath}")
        return str(filepath)

    def generate_text_report(self, filename: str = None) -> str:
        """
        Generate a text assessment report.

        Args:
            filename: Optional filename

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"uac_report_{timestamp}.txt"

        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("UAC BYPASS ASSESSMENT REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # System info
            f.write("SYSTEM INFORMATION\n")
            f.write("-" * 70 + "\n")
            info = self.detector.get_full_info()
            f.write(f"  Windows Version: {info.get('version_name', 'Unknown')}\n")
            f.write(f"  Build Number: {info.get('build_number', 'Unknown')}\n")
            f.write(f"  Edition: {info.get('edition', 'Unknown')}\n")
            f.write(f"  Architecture: {'64-bit' if info.get('is_64bit') else '32-bit'}\n\n")

            # UAC status
            f.write("UAC STATUS\n")
            f.write("-" * 70 + "\n")
            status = self.checker.get_status()
            f.write(f"  Administrator: {'Yes' if status['is_admin'] else 'No'}\n")
            f.write(f"  UAC Enabled: {'Yes' if status['uac_enabled'] else 'No'}\n")
            f.write(f"  UAC Level: {status['uac_level']} - {status['uac_level_name']}\n")
            f.write(f"  Can Bypass: {'Yes' if status['can_bypass'] else 'No'}\n\n")

            # Compatible methods
            f.write("COMPATIBLE BYPASS METHODS\n")
            f.write("-" * 70 + "\n")

            methods = self.selector.get_compatible_methods()

            if methods:
                for i, method in enumerate(methods, 1):
                    f.write(f"\n  [{i}] {method['name'].upper()}\n")
                    f.write(f"      Description: {method['description']}\n")
                    f.write(f"      Detection Risk: {method['detection_risk']}\n")
                    f.write(f"      Success Rate: {method['success_rate'] * 100:.0f}%\n")

                best = self.selector.select_best_method()
                f.write(f"\n  RECOMMENDED: {best}\n")
            else:
                f.write("  No compatible methods found.\n")
                f.write("  System may be fully patched against known UAC bypasses.\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")

        print(f"[+] Report saved: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_json_report()
    generator.generate_text_report()