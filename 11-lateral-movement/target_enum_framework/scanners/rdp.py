"""
RDP Scanner using nmap
Discover Remote Desktop targets
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseScanner
from ..core.models import Protocol, HostInfo, OperatingSystem
from ..utils.network import extract_ips_from_text


class RDPScanner(BaseScanner):
    """
    RDP Scanner using nmap

    Discovers hosts with RDP (port 3389) open.
    Targets for:
        - Standard RDP connections
        - Pass-the-Hash RDP (Restricted Admin mode)
        - BlueKeep exploitation (if vulnerable)

    RDP is common on:
        - Windows servers
        - Administrator workstations
        - Jump hosts

    OPSEC Note:
        - RDP connections are heavily logged
        - Event ID 4624 (Type 10)
        - Network Level Authentication may be required
        - Consider using Restricted Admin for PTH
    """

    protocol = Protocol.RDP
    default_port = 3389

    def build_command(self, network: str) -> str:
        """
        Build nmap RDP scan command

        Uses grepable output for easy parsing
        """
        return f"nmap -p 3389 --open {network} -oG -"

    def parse_output(self, output_text: str) -> List[HostInfo]:
        """
        Parse nmap grepable output

        Example output:
            Host: 192.168.1.10 ()    Ports: 3389/open/tcp//ms-wbt-server//
        """
        hosts = []
        seen_ips = set()

        for line in output_text.split('\n'):
            # Look for open port indicator
            if '3389/open' not in line:
                continue

            # Parse nmap grepable format
            parts = line.split()

            # Find IP address (usually after "Host:")
            for i, part in enumerate(parts):
                if part == 'Host:' and i + 1 < len(parts):
                    ip = parts[i + 1]

                    if ip in seen_ips:
                        continue

                    # Validate it's an IP
                    if ip.count('.') == 3:
                        seen_ips.add(ip)

                        # RDP is Windows
                        host = HostInfo(
                            ip=ip,
                            os=OperatingSystem.WINDOWS,
                            protocols=[Protocol.RDP],
                            ports=[3389],
                            raw_output=line.strip()
                        )

                        hosts.append(host)
                    break

        return hosts