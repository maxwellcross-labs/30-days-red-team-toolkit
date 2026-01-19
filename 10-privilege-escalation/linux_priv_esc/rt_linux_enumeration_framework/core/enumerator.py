"""
Linux Privilege Escalation Enumerator
=====================================

Main orchestrator for automated Linux privilege escalation enumeration.
Coordinates all individual enumerators and generates comprehensive reports.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Type

from .config import Config
from .findings import FindingsCollection, FindingSeverity
from .base import BaseEnumerator
from ..enumerators import ENUMERATOR_CLASSES


class LinuxPrivEscEnumerator:
    """
    Main privilege escalation enumeration orchestrator.

    Coordinates all enumeration modules and generates reports.

    Usage:
        enumerator = LinuxPrivEscEnumerator()
        enumerator.run_all()
        enumerator.generate_report()
    """

    BANNER = '''
    ╔═══════════════════════════════════════════════════════════════╗
    ║     Linux Privilege Escalation Enumerator                     ║
    ║     Part of: 30 Days of Red Team Toolkit                      ║
    ║─────────────────────────────────────────────────────────────────║
    ║     "Find the path. Escalate. Own the box."                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    '''

    def __init__(
            self,
            config: Optional[Config] = None,
            output_dir: Optional[str] = None
    ):
        """
        Initialize the enumerator.

        Args:
            config: Configuration object (created if not provided)
            output_dir: Output directory path (overrides config)
        """
        self.config = config or Config()

        if output_dir:
            self.config.output_dir = Path(output_dir)
            self.config.output_dir.mkdir(exist_ok=True, mode=0o755)

        self.findings = FindingsCollection()
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Initialize all enumerators
        self.enumerators: List[BaseEnumerator] = [
            enum_class(self.config, self.findings)
            for enum_class in ENUMERATOR_CLASSES
        ]

        print(self.BANNER)
        print(f"[+] Output directory: {self.config.output_dir}")
        print(f"[+] Loaded {len(self.enumerators)} enumeration modules")

    def run_all(self) -> None:
        """Run all enumeration modules"""
        self.start_time = datetime.now()

        print(f"\n{'=' * 60}")
        print(f"STARTING AUTOMATED ENUMERATION")
        print(f"{'=' * 60}")
        print(f"[*] Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        for enumerator in self.enumerators:
            try:
                enumerator.enumerate()
            except Exception as e:
                print(f"[-] Error in {enumerator.name}: {e}")
                if self.config.verbose:
                    import traceback
                    traceback.print_exc()

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        print(f"\n{'=' * 60}")
        print(f"ENUMERATION COMPLETE")
        print(f"{'=' * 60}")
        print(f"[*] End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Duration: {duration:.2f} seconds")

    def run_specific(self, enumerator_names: List[str]) -> None:
        """
        Run specific enumeration modules.

        Args:
            enumerator_names: List of enumerator names to run
        """
        self.start_time = datetime.now()

        for enumerator in self.enumerators:
            if enumerator.name.lower() in [n.lower() for n in enumerator_names]:
                try:
                    enumerator.enumerate()
                except Exception as e:
                    print(f"[-] Error in {enumerator.name}: {e}")

        self.end_time = datetime.now()

    def generate_report(self) -> Path:
        """
        Generate comprehensive privilege escalation report.

        Returns:
            Path to the generated report
        """
        print(f"\n{'=' * 60}")
        print(f"PRIVILEGE ESCALATION REPORT")
        print(f"{'=' * 60}")

        counts = self.findings.count_by_severity()

        print(f"\n[*] Total findings:")
        print(f"    CRITICAL: {counts['critical']} (Exploit these first!)")
        print(f"    HIGH:     {counts['high']}")
        print(f"    MEDIUM:   {counts['medium']}")
        print(f"    LOW:      {counts['low']}")
        print(f"    INFO:     {counts['info']}")

        # Print critical findings
        critical_findings = self.findings.get_critical()

        if critical_findings:
            print(f"\n{'=' * 60}")
            print(f"CRITICAL FINDINGS - EXPLOIT THESE FIRST!")
            print(f"{'=' * 60}")

            for i, finding in enumerate(critical_findings, 1):
                print(f"\n[{i}] {finding.category}")
                print(f"    Target: {finding.target or 'N/A'}")
                print(f"    Finding: {finding.finding}")
                print(f"    Exploitation:")
                for line in finding.exploitation.split('\n'):
                    print(f"      {line}")

        # Save JSON report
        report_path = self._save_json_report()

        # Save text report
        self._save_text_report()

        # Save exploitation guide
        self._save_exploitation_guide()

        return report_path

    def _save_json_report(self) -> Path:
        """Save findings to JSON file"""
        import json

        report_file = self.config.output_dir / "privesc_report.json"

        report_data = {
            'metadata': {
                'tool': 'Linux Privilege Escalation Enumerator',
                'series': '30 Days of Red Team',
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'hostname': os.uname().nodename,
                'user': os.environ.get('USER', 'unknown')
            },
            'summary': self.findings.count_by_severity(),
            'findings': self.findings.to_dict()
        }

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n[+] JSON report saved: {report_file}")

        return report_file

    def _save_text_report(self) -> Path:
        """Save findings to text file"""
        report_file = self.config.output_dir / "privesc_report.txt"

        with open(report_file, 'w') as f:
            f.write("LINUX PRIVILEGE ESCALATION REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Hostname: {os.uname().nodename}\n")
            f.write(f"User: {os.environ.get('USER', 'unknown')}\n\n")

            counts = self.findings.count_by_severity()
            f.write("SUMMARY\n")
            f.write("-" * 60 + "\n")
            f.write(f"Critical: {counts['critical']}\n")
            f.write(f"High: {counts['high']}\n")
            f.write(f"Medium: {counts['medium']}\n")
            f.write(f"Low: {counts['low']}\n")
            f.write(f"Info: {counts['info']}\n\n")

            for severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH,
                             FindingSeverity.MEDIUM, FindingSeverity.LOW]:
                findings = self.findings.get_by_severity(severity)

                if findings:
                    f.write(f"\n{severity.value.upper()} FINDINGS\n")
                    f.write("-" * 60 + "\n\n")

                    for finding in findings:
                        f.write(f"{finding}\n\n")

        print(f"[+] Text report saved: {report_file}")

        return report_file

    def _save_exploitation_guide(self) -> Path:
        """Save quick exploitation guide"""
        guide_file = self.config.output_dir / "exploitation_guide.txt"

        critical_findings = self.findings.get_critical()

        with open(guide_file, 'w') as f:
            f.write("PRIVILEGE ESCALATION EXPLOITATION GUIDE\n")
            f.write("=" * 60 + "\n\n")

            if not critical_findings:
                f.write("No critical findings - check high-severity findings.\n")
            else:
                f.write(f"Found {len(critical_findings)} critical escalation paths!\n\n")

                for i, finding in enumerate(critical_findings, 1):
                    f.write(f"[{i}] {finding.category}\n")
                    f.write(f"Target: {finding.target or 'N/A'}\n")
                    f.write(f"Exploitation:\n")
                    f.write(finding.exploitation + "\n")
                    f.write("-" * 40 + "\n\n")

        print(f"[+] Exploitation guide saved: {guide_file}")

        return guide_file

    def list_enumerators(self) -> None:
        """List all available enumerators"""
        print("\nAvailable Enumerators:")
        print("-" * 40)

        for enumerator in self.enumerators:
            print(f"  - {enumerator.name}")
            print(f"    {enumerator.description}")