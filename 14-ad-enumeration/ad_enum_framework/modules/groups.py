"""
Group enumeration module
"""

from ldap3 import SUBTREE
from ..core.config import PRIVILEGED_GROUPS, GROUP_ATTRIBUTES


class GroupEnumerator:
    """Enumerates domain groups with focus on privileged groups"""

    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
        self.groups = []

    def enumerate(self):
        """Enumerate domain groups"""
        print(f"\n{'=' * 60}")
        print(f"GROUP ENUMERATION")
        print(f"{'=' * 60}")

        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=group)',
                search_scope=SUBTREE,
                attributes=GROUP_ATTRIBUTES
            )

            group_count = 0
            for entry in self.conn.entries:
                group_info = {
                    'name': str(entry.sAMAccountName),
                    'members': [str(m) for m in entry.get('member', [])],
                    'memberof': [str(g) for g in entry.get('memberOf', [])],
                    'description': str(entry.get('description', ''))
                }
                self.groups.append(group_info)
                group_count += 1

            print(f"[+] Enumerated {group_count} groups")

            # Display privileged group membership
            self._display_privileged_groups()

        except Exception as e:
            print(f"[-] Group enumeration failed: {e}")

        return {'groups': self.groups}

    def _display_privileged_groups(self):
        """Display membership of privileged groups"""
        print(f"\n[*] Privileged Group Membership:")

        for priv_group in PRIVILEGED_GROUPS:
            for group in self.groups:
                if group['name'].lower() == priv_group.lower():
                    member_count = len(group['members'])
                    print(f"    {group['name']}: {member_count} members")

                    # Show first 5 members
                    for member in group['members'][:5]:
                        cn = member.split(',')[0].replace('CN=', '')
                        print(f"        - {cn}")

                    if member_count > 5:
                        print(f"        ... and {member_count - 5} more")
                    break