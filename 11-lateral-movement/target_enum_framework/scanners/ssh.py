"""
SSH Scanner using nmap
Discover Linux/Unix lateral movement targets
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseScanner
from ..core.models import Protocol, HostInfo, OperatingSystem
from ..utils.network import extract_ips_from_text


class SSHScanner(BaseScanner):
    """
    SSH Scanner using nmap

    Discovers hosts with SSH (port 22) open.
    Primary targets for Linux lateral movement:
        - Key-based authentication
        - Password spraying
        - Credential reuse

    SSH is common on:
        - Linux servers
        - Network devices
        - IoT devices
        - BSD systems

    OPSEC Note:
        - SSH attempts logged in /var/log/auth.log
        - Failed attempts may trigger fail2ban
        - Key-based auth is stealthier than password
        - Consider tunneling through SSH for pivoting
    """

    protocol = Protocol.SSH
    default_port = 22

    def build_command(self, network: str) -> str:
        """
        Build nmap SSH scan command

        Uses grepable output for easy parsing
        """
        return f"nmap -p 22 --open {network} -oG -"

    def parse_output(self, output_text: str) -> List[HostInfo]:
        """
        Parse nmap grepable output

        Example output:
            Host: 192.168.1.50 ()    Ports: 22/open/tcp//ssh//
        """
        hosts = []
        seen_ips = set()

        for line in output_text.split('\n'):
            # Look for open port indicator
            if '22/open' not in line:
                continue

            # Parse nmap grepable format
            parts = line.split()

            # Find IP address
            for i, part in enumerate(parts):
                if part == 'Host:' and i + 1 < len(parts):
                    ip = parts[i + 1]

                    if ip in seen_ips:
                        continue

                    # Validate it's an IP
                    if ip.count('.') == 3:
                        seen_ips.add(ip)

                        # SSH is typically Linux
                        host = HostInfo(
                            ip=ip,
                            os=OperatingSystem.LINUX,
                            protocols=[Protocol.SSH],
                            ports=[22],
                            raw_output=line.strip()
                        )

                        hosts.append(host)
                    break

        return hosts