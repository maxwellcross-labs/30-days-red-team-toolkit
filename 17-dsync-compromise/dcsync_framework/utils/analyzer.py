"""
Credential Analyzer — Analyze DCSync dumps for password patterns,
reuse, empty passwords, and high-value account identification.
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CredentialAnalyzer:
    """Analyze NTDS dump files for credential weaknesses."""

    EMPTY_LM = "aad3b435b51404eeaad3b435b51404ee"
    EMPTY_NT = "31d6cfe0d16ae931b73c59d7e0c089c0"

    HIGH_VALUE_KEYWORDS = ["admin", "krbtgt", "svc_", "backup", "sql"]

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def analyze(self, ntds_file: str):
        """Run full credential analysis on a .ntds hash file."""
        print(f"\n{'=' * 60}")
        print("CREDENTIAL ANALYSIS")
        print(f"{'=' * 60}")

        if not os.path.exists(ntds_file):
            print(f"[-] File not found: {ntds_file}")
            return

        hashes, hash_counts, user_accounts, machine_accounts, empty_accounts = (
            self._parse_file(ntds_file)
        )

        self._print_statistics(
            hashes, hash_counts, user_accounts, machine_accounts, empty_accounts
        )
        self._print_reuse_analysis(hashes, hash_counts)
        self._print_empty_passwords(empty_accounts)
        self._print_high_value(hashes)
        self._save_analysis(
            hashes, hash_counts, user_accounts, machine_accounts, empty_accounts
        )

    def _parse_file(self, ntds_file: str):
        """Parse the .ntds file into structured data."""
        hashes: Dict[str, dict] = {}
        hash_counts: Dict[str, int] = defaultdict(int)
        user_accounts: List[str] = []
        machine_accounts: List[str] = []
        empty_accounts: List[str] = []

        with open(ntds_file) as f:
            for line in f:
                line = line.strip()
                if ":::" not in line:
                    continue

                parts = line.split(":")
                if len(parts) < 4:
                    continue

                username, rid, lm_hash, nt_hash = (
                    parts[0], parts[1], parts[2], parts[3],
                )

                hashes[username] = {
                    "username": username,
                    "rid": rid,
                    "lm_hash": lm_hash,
                    "nt_hash": nt_hash,
                }
                hash_counts[nt_hash] += 1

                if "$" in username:
                    machine_accounts.append(username)
                else:
                    user_accounts.append(username)

                if nt_hash == self.EMPTY_NT:
                    empty_accounts.append(username)

        return hashes, hash_counts, user_accounts, machine_accounts, empty_accounts

    @staticmethod
    def _print_statistics(hashes, hash_counts, user_accounts, machine_accounts, empty_accounts):
        print(f"\n[*] Overall Statistics:")
        print(f"    Total accounts: {len(hashes)}")
        print(f"    User accounts: {len(user_accounts)}")
        print(f"    Machine accounts: {len(machine_accounts)}")
        print(f"    Unique password hashes: {len(hash_counts)}")
        print(f"    Empty passwords: {len(empty_accounts)}")

    def _print_reuse_analysis(self, hashes, hash_counts):
        print(f"\n[*] Password Reuse Analysis:")

        reused = {
            h: c for h, c in hash_counts.items()
            if c > 1 and h != self.EMPTY_NT
        }

        if not reused:
            print("    No password reuse detected (unusual)")
            return

        sorted_reuse = sorted(reused.items(), key=lambda x: x[1], reverse=True)
        for nt_hash, count in sorted_reuse[:15]:
            users = [
                u for u, e in hashes.items()
                if e["nt_hash"] == nt_hash and "$" not in u
            ]
            if users:
                print(f"    Hash ...{nt_hash[-8:]} used by {count} accounts:")
                for u in users[:5]:
                    print(f"        {u}")
                if len(users) > 5:
                    print(f"        ... and {len(users) - 5} more")

    @staticmethod
    def _print_empty_passwords(empty_accounts):
        user_empties = [a for a in empty_accounts if "$" not in a]
        if user_empties:
            print(f"\n[!] EMPTY PASSWORD ACCOUNTS:")
            for acct in user_empties:
                print(f"    ★ {acct} — NO PASSWORD SET!")

    def _print_high_value(self, hashes):
        print(f"\n[*] High-Value Account Hashes:")
        for user, entry in hashes.items():
            is_hv = any(kw in user.lower() for kw in self.HIGH_VALUE_KEYWORDS)
            if is_hv and "$" not in user:
                print(f"    ★ {user}:{entry['rid']}:{entry['nt_hash']}")

    def _save_analysis(self, hashes, hash_counts, user_accounts, machine_accounts, empty_accounts):
        reused = {h: c for h, c in hash_counts.items() if c > 1 and h != self.EMPTY_NT}

        analysis = {
            "total_accounts": len(hashes),
            "user_accounts": len(user_accounts),
            "machine_accounts": len(machine_accounts),
            "unique_hashes": len(hash_counts),
            "empty_passwords": [a for a in empty_accounts if "$" not in a],
            "password_reuse_count": len(reused),
            "most_reused_hash_count": max(reused.values()) if reused else 0,
            "timestamp": datetime.now().isoformat(),
        }

        analysis_file = self.output_dir / "credential_analysis.json"
        analysis_file.write_text(json.dumps(analysis, indent=2))
        print(f"\n[+] Analysis saved: {analysis_file}")