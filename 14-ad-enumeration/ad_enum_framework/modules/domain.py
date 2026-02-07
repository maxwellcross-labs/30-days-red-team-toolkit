"""
Domain information enumeration module
"""

from ldap3 import SUBTREE


class DomainEnumerator:
    """Enumerates basic domain information"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.domain = ldap_conn.domain
        self.dc_ip = ldap_conn.dc_ip
        self.results = {}

    def enumerate(self):
        """Get basic domain information and domain controllers"""
        print(f"\n{'=' * 60}")
        print(f"DOMAIN INFORMATION")
        print(f"{'=' * 60}")

        try:
            # Get domain object
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=domain)',
                search_scope=SUBTREE,
                attributes=['*']
            )

            if self.conn.entries:
                domain_obj = self.conn.entries[0]
                self.results = {
                    'name': self.domain,
                    'dn': str(domain_obj.entry_dn),
                    'dc_ip': self.dc_ip
                }
                print(f"[+] Domain: {self.domain}")

                # Enumerate domain controllers
                self._enumerate_domain_controllers()

        except Exception as e:
            print(f"[-] Domain info enumeration failed: {e}")

        return self.results

    def _enumerate_domain_controllers(self):
        """Query all domain controllers"""
        try:
            # UserAccountControl flag 8192 = SERVER_TRUST_ACCOUNT (Domain Controller)
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))',
                search_scope=SUBTREE,
                attributes=['name', 'dNSHostName', 'operatingSystem']
            )

            dcs = []
            for entry in self.conn.entries:
                dc_info = {
                    'name': str(entry.name),
                    'hostname': str(entry.get('dNSHostName', '')),
                    'os': str(entry.get('operatingSystem', ''))
                }
                dcs.append(dc_info)
                print(f"[+] DC: {dc_info['name']} ({dc_info['os']})")

            self.results['domain_controllers'] = dcs

        except Exception as e:
            print(f"[-] DC enumeration failed: {e}")
