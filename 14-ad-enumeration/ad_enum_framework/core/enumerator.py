"""
Main AD Enumeration orchestrator
"""

from connection import LDAPConnection
from ..modules.domain import DomainEnumerator
from ..modules.users import UserEnumerator
from ..modules.groups import GroupEnumerator
from ..modules.computers import ComputerEnumerator
from ..modules.spns import SPNEnumerator
from ..modules.trusts import TrustEnumerator
from ..utils.reporter import ReportGenerator


class ADEnumerator:
    """Main orchestrator for AD enumeration"""

    def __init__(self, domain, username, password, dc_ip=None, output_dir="ad_enum"):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip
        self.output_dir = output_dir

        # Initialize connection
        self.ldap_conn = LDAPConnection(domain, username, password, dc_ip)

        # Initialize modules
        self.domain_enum = None
        self.user_enum = None
        self.group_enum = None
        self.computer_enum = None
        self.spn_enum = None
        self.trust_enum = None

        # Results
        self.results = {}

        print(f"[+] AD Enumerator initialized")
        print(f"[+] Domain: {self.domain}")
        print(f"[+] Output: {self.output_dir}")

    def run_full_enumeration(self):
        """Run complete AD enumeration"""
        print(f"\n{'#' * 60}")
        print(f"# ACTIVE DIRECTORY ENUMERATION")
        print(f"# Target: {self.domain}")
        print(f"{'#' * 60}")

        # Connect to domain
        if not self.ldap_conn.connect():
            return False

        # Initialize all enumeration modules
        self._initialize_modules()

        # Run all enumeration tasks
        self._run_enumeration()

        # Generate reports
        self._generate_reports()

        # Cleanup
        self.ldap_conn.disconnect()

        print(f"\n{'=' * 60}")
        print(f"ENUMERATION COMPLETE")
        print(f"{'=' * 60}")
        return True

    def _initialize_modules(self):
        """Initialize all enumeration modules"""
        self.domain_enum = DomainEnumerator(self.ldap_conn)
        self.user_enum = UserEnumerator(self.ldap_conn)
        self.group_enum = GroupEnumerator(self.ldap_conn)
        self.computer_enum = ComputerEnumerator(self.ldap_conn)
        self.spn_enum = SPNEnumerator(self.ldap_conn)
        self.trust_enum = TrustEnumerator(self.ldap_conn)

    def _run_enumeration(self):
        """Execute all enumeration modules"""
        # Domain information
        domain_results = self.domain_enum.enumerate()
        self.results['domain_info'] = domain_results

        # Users
        user_results = self.user_enum.enumerate()
        self.results.update(user_results)

        # Groups
        group_results = self.group_enum.enumerate()
        self.results.update(group_results)

        # Computers
        computer_results = self.computer_enum.enumerate()
        self.results.update(computer_results)

        # SPNs
        spn_results = self.spn_enum.enumerate()
        self.results.update(spn_results)

        # Trusts
        trust_results = self.trust_enum.enumerate()
        self.results.update(trust_results)

    def _generate_reports(self):
        """Generate all reports"""
        reporter = ReportGenerator(self.output_dir, self.domain)
        reporter.set_results(self.results)
        reporter.generate_all_reports()