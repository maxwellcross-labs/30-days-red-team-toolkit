"""
Domain SID Resolver — Retrieves the domain SID required for ticket forging.

Attempts Impacket lookupsid.py first, falls back to rpcclient.
The domain SID is a prerequisite for Golden and Silver Ticket attacks.
"""

import subprocess
from typing import Optional


class SIDResolver:
    """Resolve the domain SID via Impacket or rpcclient."""

    def __init__(self, domain: str, dc_ip: str):
        self.domain = domain
        self.dc_ip = dc_ip

    def resolve(
        self,
        username: str,
        password: str = "",
        ntlm_hash: str = "",
    ) -> str:
        """
        Retrieve the domain SID. Tries lookupsid.py, then rpcclient.

        Returns the SID string or empty string on failure.
        """
        print(f"\n{'=' * 60}")
        print("GATHERING DOMAIN SID")
        print(f"{'=' * 60}")

        if not password and not ntlm_hash:
            print("[-] Need password or hash")
            return ""

        sid = self._try_lookupsid(username, password, ntlm_hash)
        if sid:
            return sid

        print("[*] Trying alternative SID lookup...")
        sid = self._try_rpcclient(username, password, ntlm_hash)
        if sid:
            return sid

        print("[-] Could not retrieve Domain SID")
        print(f"[*] Manual: rpcclient -U 'user%pass' {self.dc_ip} -c 'lsaquery'")
        return ""

    def _try_lookupsid(
        self, username: str, password: str, ntlm_hash: str
    ) -> str:
        """Attempt SID lookup via Impacket lookupsid.py."""
        if password:
            cmd = [
                "lookupsid.py",
                f"{self.domain}/{username}:{password}@{self.dc_ip}",
            ]
        else:
            cmd = [
                "lookupsid.py",
                f"{self.domain}/{username}@{self.dc_ip}",
                "-hashes", f":{ntlm_hash}",
            ]

        try:
            print(f"[*] Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.splitlines():
                if "Domain SID is:" in line:
                    sid = line.split("Domain SID is:")[1].strip()
                    print(f"[+] Domain SID: {sid}")
                    return sid
        except FileNotFoundError:
            print("[-] lookupsid.py not found — install Impacket")
        except Exception as e:
            print(f"[-] SID lookup failed: {e}")

        return ""

    def _try_rpcclient(
        self, username: str, password: str, ntlm_hash: str
    ) -> str:
        """Fallback SID lookup via rpcclient."""
        if password:
            cmd = [
                "rpcclient", "-U", f"{username}%{password}",
                self.dc_ip, "-c", "lsaquery",
            ]
        else:
            cmd = [
                "rpcclient", "-U", f"{username}%", "--pw-nt-hash",
                self.dc_ip, "-c", "lsaquery",
            ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            for line in result.stdout.splitlines():
                if "Domain Sid:" in line:
                    sid = line.split("Domain Sid:")[1].strip()
                    print(f"[+] Domain SID: {sid}")
                    return sid
        except Exception as e:
            print(f"[-] rpcclient failed: {e}")

        return ""