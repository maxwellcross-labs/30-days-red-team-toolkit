"""
Report generation utilities
"""

import json
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Generates enumeration reports in various formats"""

    def __init__(self, output_dir, domain):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.domain = domain
        self.results = {}

    def set_results(self, results):
        """Set the enumeration results"""
        self.results = results

    def generate_all_reports(self):
        """Generate all report formats"""
        print(f"\n{'=' * 60}")
        print(f"GENERATING REPORTS")
        print(f"{'=' * 60}")

        self.generate_json_report()
        self.generate_user_list()
        self.generate_kerberoast_list()
        self.generate_summary()

        print(f"\n[+] All reports generated in: {self.output_dir}")

    def generate_json_report(self):
        """Generate comprehensive JSON report"""
        report_file = self.output_dir / "ad_enum_report.json"

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"[+] JSON report: {report_file}")

    def generate_user_list(self):
        """Generate simple user list"""
        users_file = self.output_dir / "users.txt"

        with open(users_file, 'w') as f:
            for user in self.results.get('users', []):
                f.write(f"{user['samaccountname']}\n")

        print(f"[+] User list: {users_file}")

    def generate_kerberoast_list(self):
        """Generate Kerberoastable users list"""
        kerberoastable = self.results.get('kerberoastable', [])

        if kerberoastable:
            kerb_file = self.output_dir / "kerberoastable.txt"

            with open(kerb_file, 'w') as f:
                for user in kerberoastable:
                    f.write(f"{user['samaccountname']}\t{user['spns'][0]}\n")

            print(f"[+] Kerberoastable users: {kerb_file}")

    def generate_summary(self):
        """Generate executive summary"""
        summary_file = self.output_dir / "summary.txt"

        with open(summary_file, 'w') as f:
            f.write(f"AD Enumeration Summary - {self.domain}\n")
            f.write(f"{'=' * 50}\n")
            f.write(f"Enumeration Time: {datetime.now().isoformat()}\n\n")

            f.write(f"Total Objects:\n")
            f.write(f"  Users: {len(self.results.get('users', []))}\n")
            f.write(f"  Computers: {len(self.results.get('computers', []))}\n")
            f.write(f"  Groups: {len(self.results.get('groups', []))}\n")
            f.write(f"  Trusts: {len(self.results.get('trusts', []))}\n\n")

            f.write(f"Attack Targets:\n")
            f.write(f"  Privileged Users: {len(self.results.get('privileged_users', []))}\n")
            f.write(f"  Kerberoastable: {len(self.results.get('kerberoastable', []))}\n")
            f.write(f"  AS-REP Roastable: {len(self.results.get('asreproastable', []))}\n")
            f.write(f"  Unconstrained Delegation: {len(self.results.get('unconstrained_delegation', []))}\n")
            f.write(f"  Constrained Delegation: {len(self.results.get('constrained_delegation', []))}\n")

        print(f"[+] Executive summary: {summary_file}")