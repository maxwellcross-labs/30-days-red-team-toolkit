"""
Report Generator — Produces JSON and plaintext summaries
of the roasting engagement results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from ..core.target import RoastingTarget


class ReportGenerator:
    """Generate engagement reports from roasting results."""

    def __init__(self, domain: str, output_dir: Path):
        self.domain = domain
        self.output_dir = output_dir

    def generate(
        self,
        targets: List[RoastingTarget],
        kerberoastable: List[RoastingTarget],
        asreproastable: List[RoastingTarget],
        hashes: List[str],
    ):
        """Write JSON report and plaintext summary."""
        print(f"\n{'=' * 60}")
        print("GENERATING REPORT")
        print(f"{'=' * 60}")

        self._write_json(targets, kerberoastable, asreproastable, hashes)
        self._write_summary(kerberoastable, asreproastable, hashes)

    def _write_json(self, targets, kerberoastable, asreproastable, hashes):
        report = {
            "domain": self.domain,
            "timestamp": datetime.now().isoformat(),
            "kerberoastable": len(kerberoastable),
            "asreproastable": len(asreproastable),
            "hashes_extracted": len(hashes),
            "targets": [
                {
                    "username": t.username,
                    "type": t.roast_type,
                    "priority": t.priority,
                    "is_admin": t.is_admin,
                    "spns": t.spns,
                    "pwd_last_set": t.pwd_last_set,
                }
                for t in targets
            ],
        }
        report_file = self.output_dir / "roasting_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"[+] JSON report: {report_file}")

    def _write_summary(self, kerberoastable, asreproastable, hashes):
        summary_file = self.output_dir / "summary.txt"
        with open(summary_file, "w") as f:
            f.write(f"Roasting Summary — {self.domain}\n{'=' * 50}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n\n")
            f.write(f"Kerberoastable: {len(kerberoastable)}\n")
            f.write(f"AS-REP Roastable: {len(asreproastable)}\n")
            f.write(f"Hashes Extracted: {len(hashes)}\n")
        print(f"[+] Summary: {summary_file}")