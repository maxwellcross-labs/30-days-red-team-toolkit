"""
User enumeration module
"""

from ldap3 import SUBTREE
from ..core.config import USER_ATTRIBUTES, UAC_FLAGS, PASSWORD_KEYWORDS


class UserEnumerator:
    """Enumerates domain users and identifies attack vectors"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.users = []
        self.privileged_users = []
        self.kerberoastable = []
        self.asreproastable = []

    def enumerate(self):
        """Enumerate all domain users"""
        print(f"\n{'=' * 60}")
        print(f"USER ENUMERATION")
        print(f"{'=' * 60}")

        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(&(objectClass=user)(objectCategory=person))',
                search_scope=SUBTREE,
                attributes=USER_ATTRIBUTES
            )

            user_count = 0
            for entry in self.conn.entries:
                user_info = self._parse_user_entry(entry)
                self.users.append(user_info)
                user_count += 1

                # Categorize users
                self._categorize_user(user_info)

            self._print_summary()

        except Exception as e:
            print(f"[-] User enumeration failed: {e}")

        return {
            'users': self.users,
            'privileged_users': self.privileged_users,
            'kerberoastable': self.kerberoastable,
            'asreproastable': self.asreproastable
        }

    def _parse_user_entry(self, entry):
        """Parse LDAP entry into user info dictionary"""
        return {
            'samaccountname': str(entry.sAMAccountName),
            'upn': str(entry.get('userPrincipalName', '')),
            'displayname': str(entry.get('displayName', '')),
            'description': str(entry.get('description', '')),
            'memberof': [str(g) for g in entry.get('memberOf', [])],
            'admincount': str(entry.get('adminCount', 0)),
            'spns': [str(s) for s in entry.get('servicePrincipalName', [])],
            'uac': int(str(entry.get('userAccountControl', 0)))
        }

    def _categorize_user(self, user_info):
        """Categorize user based on attributes"""
        # Privileged users (adminCount = 1)
        if user_info['admincount'] == '1':
            self.privileged_users.append(user_info)

        # Kerberoastable (has SPNs)
        if user_info['spns']:
            self.kerberoastable.append(user_info)

        # AS-REP Roastable (DONT_REQ_PREAUTH flag)
        if user_info['uac'] & UAC_FLAGS['DONT_REQ_PREAUTH']:
            self.asreproastable.append(user_info)

        # Check for passwords in description
        desc_lower = user_info['description'].lower()
        if any(word in desc_lower for word in PASSWORD_KEYWORDS):
            print(f"[!] Potential password in description: {user_info['samaccountname']}")
            print(f"    Description: {user_info['description']}")

    def _print_summary(self):
        """Print enumeration summary"""
        print(f"[+] Enumerated {len(self.users)} users")
        print(f"[+] Privileged users (adminCount=1): {len(self.privileged_users)}")
        print(f"[+] Kerberoastable users: {len(self.kerberoastable)}")
        print(f"[+] AS-REP Roastable users: {len(self.asreproastable)}")

        if self.kerberoastable:
            print(f"\n[*] Kerberoastable Users:")
            for user in self.kerberoastable[:10]:  # Show first 10
                print(f"    {user['samaccountname']}: {user['spns'][0]}")
            if len(self.kerberoastable) > 10:
                print(f"    ... and {len(self.kerberoastable) - 10} more")