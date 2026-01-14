import json
from pathlib import Path


class Reporter:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.findings = {
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

    def add_finding(self, severity, data):
        if severity in self.findings:
            self.findings[severity].append(data)

    def generate_report(self):
        print(f"\n" + "=" * 60)
        print(f"PRIVILEGE ESCALATION ENUMERATION REPORT")
        print(f"=" * 60)

        high_count = len(self.findings['high'])
        medium_count = len(self.findings['medium'])
        low_count = len(self.findings['low'])

        print(f"\n[*] Total findings:")
        print(f"    HIGH:   {high_count} (Exploit these first!)")
        print(f"    MEDIUM: {medium_count}")
        print(f"    LOW:    {low_count}")

        if high_count > 0:
            print(f"\n" + "=" * 60)
            print(f"HIGH PRIORITY FINDINGS (Exploit These First!)")
            print(f"=" * 60)

            for i, finding in enumerate(self.findings['high'], 1):
                print(f"\n[{i}] {finding['category']}")
                for key, value in finding.items():
                    if key != 'category':
                        print(f"    {key}: {value}")

        self._save_json()
        self._create_guide(high_count)

    def _save_json(self):
        report_file = self.output_dir / "privesc_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.findings, f, indent=2)
        print(f"\n[+] Full report saved to: {report_file}")

    def _create_guide(self, high_count):
        guide_file = self.output_dir / "exploitation_guide.txt"
        with open(guide_file, 'w') as f:
            f.write("PRIVILEGE ESCALATION EXPLOITATION GUIDE\n")
            f.write("=" * 60 + "\n\n")

            if high_count > 0:
                f.write("HIGH PRIORITY TARGETS:\n")
                f.write("-" * 60 + "\n\n")
                for finding in self.findings['high']:
                    f.write(f"Category: {finding['category']}\n")
                    f.write(f"Exploitation: {finding.get('exploitation', 'N/A')}\n")
                    f.write(f"Impact: {finding.get('impact', 'N/A')}\n")
                    f.write("\n")
        print(f"[+] Exploitation guide saved to: {guide_file}")