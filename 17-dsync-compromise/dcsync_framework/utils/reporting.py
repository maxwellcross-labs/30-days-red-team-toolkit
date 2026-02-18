"""
Report Generator — Produces a JSON operation report summarizing
DCSync results, extracted material, and recommended next steps.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class ReportGenerator:
    """Generate engagement reports for DCSync operations."""

    def __init__(self, domain: str, dc_ip: str, output_dir: Path):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = output_dir

    def generate(
        self,
        extracted_hashes: Dict[str, dict],
        high_value_hashes: Dict[str, dict],
        krbtgt_material: dict,
    ):
        """Write a JSON report of the DCSync operation."""
        report_file = self.output_dir / "dcsync_report.json"
        has_krbtgt = bool(krbtgt_material)

        report = {
            "domain": self.domain,
            "dc": self.dc_ip,
            "timestamp": datetime.now().isoformat(),
            "total_extracted": len(extracted_hashes),
            "high_value_extracted": len(high_value_hashes),
            "krbtgt_obtained": has_krbtgt,
            "high_value_accounts": list(high_value_hashes.keys()),
            "next_steps": [
                "Crack extracted hashes with hashcat",
                "Forge Golden Ticket with KRBTGT material"
                if has_krbtgt
                else "Obtain KRBTGT via full DCSync",
                "Test password reuse across domain",
                "Establish persistence (Day 26)",
            ],
        }

        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n[+] Report: {report_file}")