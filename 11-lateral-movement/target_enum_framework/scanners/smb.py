"""
SMB Scanner using CrackMapExec
Primary lateral movement target discovery
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseScanner
from ..core.models import Protocol, HostInfo, OperatingSystem, TargetCategory
from ..utils.network import extract_ips_from_text


class SMBScanner(BaseScanner):
    """
    SMB Scanner using CrackMapExec

    Discovers hosts with SMB (port 445) open.
    These are primary targets for lateral movement via:
        - Pass-the-Hash
        - PSExec
        - WMI

    CrackMapExec provides rich output including:
        - OS version
        - Hostname
        - Domain information
        - Signing status

    OPSEC Note:
        - SMB enumeration generates network traffic
        - May be logged by network monitoring
        - Consider using targeted scans vs. broad sweeps
    """

    protocol = Protocol.SMB
    default_port = 445

    def build_command(self, network: str) -> str:
        """
        Build CrackMapExec SMB scan command

        Also generates relay target list for potential NTLM relay attacks.
        """
        return f"crackmapexec smb {network} --gen-relay-list relay_targets.txt"

    def parse_output(self, output_text: str) -> List[HostInfo]:
        """
        Parse CrackMapExec SMB output

        Example output lines:
            SMB  192.168.1.10  445  DC01  [*] Windows Server 2019 Build 17763 x64
            SMB  192.168.1.20  445  WS01  [*] Windows 10 Build 19041 x64
        """
        hosts = []
        seen_ips = set()

        for line in output_text.split('\n'):
            if 'SMB' not in line:
                continue

            # Skip if not a host line
            if not ('Windows' in line or 'Samba' in line or 'Linux' in line):
                continue

            # Extract IP addresses from line
            ips = extract_ips_from_text(line)

            for ip in ips:
                if ip in seen_ips:
                    continue
                seen_ips.add(ip)

                # Determine OS
                line_upper = line.upper()
                if 'WINDOWS' in line_upper:
                    os_type = OperatingSystem.WINDOWS
                elif 'SAMBA' in line_upper or 'LINUX' in line_upper:
                    os_type = OperatingSystem.LINUX
                else:
                    os_type = OperatingSystem.UNKNOWN

                # Create host info
                host = HostInfo(
                    ip=ip,
                    os=os_type,
                    protocols=[Protocol.SMB],
                    ports=[445],
                    raw_output=line.strip()
                )

                # Check for Domain Controller indicators
                dc_indicators = ['DC', 'DOMAIN CONTROLLER', 'PRIMARY', 'PDC', 'BDC']
                if any(ind in line_upper for ind in dc_indicators):
                    host.add_category(TargetCategory.DOMAIN_CONTROLLER)
                    host.add_category(TargetCategory.HIGH_VALUE)

                # Extract hostname if present
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == ip and i + 2 < len(parts):
                        # Hostname is usually 2 positions after IP
                        potential_hostname = parts[i + 2]
                        if not potential_hostname.startswith('[') and not potential_hostname.isdigit():
                            host.hostname = potential_hostname
                        break

                hosts.append(host)

        return hosts