"""
Trust relationship enumeration module
"""

from ldap3 import SUBTREE
from ..core.config import TRUST_DIRECTIONS, TRUST_TYPES


class TrustEnumerator:
    """Enumerates domain trust relationships"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.trusts = []

    def enumerate(self):
        """Enumerate domain trusts"""
        print(f"\n{'=' * 60}")
        print(f"TRUST RELATIONSHIP ENUMERATION")
        print(f"{'=' * 60}")

        try:
            self.conn.search(
                search_base=f"CN=System,{self.base_dn}",
                search_filter='(objectClass=trustedDomain)',
                search_scope=SUBTREE,
                attributes=['cn', 'trustPartner', 'trustDirection', 'trustType']
            )

            if self.conn.entries:
                for entry in self.conn.entries:
                    trust_info = self._parse_trust_entry(entry)
                    self.trusts.append(trust_info)
                    self._print_trust(trust_info)

                print(f"\n[+] Total trusts: {len(self.trusts)}")
            else:
                print(f"[*] No trust relationships found")

        except Exception as e:
            print(f"[-] Trust enumeration failed: {e}")

        return {'trusts': self.trusts}

    def _parse_trust_entry(self, entry):
        """Parse trust entry into trust info dictionary"""
        direction_val = int(str(entry.trustDirection))
        type_val = int(str(entry.trustType))

        return {
            'partner': str(entry.trustPartner),
            'direction': TRUST_DIRECTIONS.get(direction_val, 'Unknown'),
            'type': TRUST_TYPES.get(type_val, 'Unknown')
        }

    def _print_trust(self, trust_info):
        """Print trust information"""
        print(f"[+] Trust: {trust_info['partner']}")
        print(f"    Direction: {trust_info['direction']}")
        print(f"    Type: {trust_info['type']}")