"""
WinRM Scanner using CrackMapExec
Discover PowerShell Remoting targets
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseScanner
from ..core.models import Protocol, HostInfo, OperatingSystem
from ..utils.network import extract_ips_from_text


class WinRMScanner(BaseScanner):
    """
    WinRM Scanner using CrackMapExec

    Discovers hosts with WinRM (ports 5985/5986) open.
    These are targets for:
        - PowerShell Remoting
        - evil-winrm
        - Enter-PSSession

    WinRM is commonly enabled on:
        - Servers (especially Server 2012+)
        - Domain-joined workstations
        - Systems managed via PowerShell

    OPSEC Note:
        - WinRM is often monitored
        - Connections logged in PowerShell logs
        - Consider using alternative methods if WinRM is heavily monitored
    """

    protocol = Protocol.WINRM
    default_port = 5985

    def build_command(self, network: str) -> str:
        """Build CrackMapExec WinRM scan command"""
        return f"crackmapexec winrm {network}"

    def parse_output(self, output_text: str) -> List[HostInfo]:
        """
        Parse CrackMapExec WinRM output

        Example output:
            WINRM  192.168.1.10  5985  DC01  [*] Windows 10.0 Build 17763
        """
        hosts = []
        seen_ips = set()

        for line in output_text.split('\n'):
            if 'WINRM' not in line:
                continue

            # Extract IPs
            ips = extract_ips_from_text(line)

            for ip in ips:
                if ip in seen_ips:
                    continue
                seen_ips.add(ip)

                # WinRM is Windows-only
                host = HostInfo(
                    ip=ip,
                    os=OperatingSystem.WINDOWS,
                    protocols=[Protocol.WINRM],
                    ports=[5985],
                    raw_output=line.strip()
                )

                hosts.append(host)

        return hosts