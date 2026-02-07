"""
Computer enumeration module
"""

from ldap3 import SUBTREE
from ..core.config import COMPUTER_ATTRIBUTES, UAC_FLAGS


class ComputerEnumerator:
    """Enumerates domain computers and identifies delegation vulnerabilities"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.computers = []
        self.unconstrained_delegation = []
        self.constrained_delegation = []

    def enumerate(self):
        """Enumerate domain computers"""
        print(f"\n{'=' * 60}")
        print(f"COMPUTER ENUMERATION")
        print(f"{'=' * 60}")

        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=computer)',
                search_scope=SUBTREE,
                attributes=COMPUTER_ATTRIBUTES
            )

            computer_count = 0
            servers = []
            workstations = []

            for entry in self.conn.entries:
                comp_info = self._parse_computer_entry(entry)
                self.computers.append(comp_info)
                computer_count += 1

                # Categorize by OS
                if 'server' in comp_info['os'].lower():
                    servers.append(comp_info)
                else:
                    workstations.append(comp_info)

                # Check for delegation vulnerabilities
                self._check_delegation(comp_info)

            print(f"[+] Enumerated {computer_count} computers")
            print(f"    Servers: {len(servers)}")
            print(f"    Workstations: {len(workstations)}")
            print(f"[+] Unconstrained Delegation: {len(self.unconstrained_delegation)}")
            print(f"[+] Constrained Delegation: {len(self.constrained_delegation)}")

        except Exception as e:
            print(f"[-] Computer enumeration failed: {e}")

        return {
            'computers': self.computers,
            'unconstrained_delegation': self.unconstrained_delegation,
            'constrained_delegation': self.constrained_delegation
        }

    def _parse_computer_entry(self, entry):
        """Parse LDAP entry into computer info dictionary"""
        return {
            'name': str(entry.sAMAccountName).rstrip('$'),
            'hostname': str(entry.get('dNSHostName', '')),
            'os': str(entry.get('operatingSystem', '')),
            'uac': int(str(entry.get('userAccountControl', 0))),
            'constrained_delegation': [str(d) for d in entry.get('msDS-AllowedToDelegateTo', [])],
            'laps_password': str(entry.get('ms-MCS-AdmPwd', ''))
        }

    def _check_delegation(self, comp_info):
        """Check for delegation vulnerabilities"""
        # Unconstrained delegation (exclude DCs)
        if comp_info['uac'] & UAC_FLAGS['TRUSTED_FOR_DELEGATION']:
            if 'Domain Controller' not in comp_info['os']:
                self.unconstrained_delegation.append(comp_info)
                print(f"[!] Unconstrained Delegation: {comp_info['name']}")

        # Constrained delegation
        if comp_info['constrained_delegation']:
            self.constrained_delegation.append(comp_info)

        # LAPS password readable
        if comp_info['laps_password'] and comp_info['laps_password'] != '[]':
            print(f"[!] LAPS Password Readable: {comp_info['name']}")