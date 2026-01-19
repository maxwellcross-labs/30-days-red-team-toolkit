"""
SUID/SGID Binary Enumerator
===========================

Discover SUID and SGID binaries for privilege escalation.

SUID (Set User ID) binaries execute with the permissions of the file owner,
typically root. If exploitable, they provide direct privilege escalation.
"""

import os
from pathlib import Path
from typing import List, Set

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class SUIDEnumerator(BaseEnumerator):
    """
    Enumerate SUID and SGID binaries on the system.

    Checks:
    - SUID binaries (execute as owner)
    - SGID binaries (execute with group)
    - Cross-references with GTFOBins
    - Identifies unusual/custom SUID binaries
    """

    name = "SUID/SGID Binary Enumerator"
    description = "Find SUID and SGID binaries for privilege escalation"

    def enumerate(self) -> None:
        """Run SUID/SGID enumeration"""
        self.print_header()

        self._enumerate_suid_binaries()
        self._enumerate_sgid_binaries()

    def _enumerate_suid_binaries(self) -> None:
        """Find and analyze SUID binaries"""
        self.log("Searching for SUID binaries (this may take a minute)...")

        # Find all SUID binaries
        output = self.run_command(
            "find / -type f -perm -4000 2>/dev/null",
            timeout=120
        )

        if not output:
            self.log("No SUID binaries found or search failed", "warning")
            return

        suid_binaries = [line.strip() for line in output.split('\n') if line.strip()]
        self.log(f"Found {len(suid_binaries)} SUID binaries", "success")

        # Categorize binaries
        exploitable: List[str] = []
        unusual: List[str] = []
        standard: List[str] = []

        for binary_path in suid_binaries:
            binary_name = os.path.basename(binary_path)

            if self.config.is_gtfobins(binary_name):
                exploitable.append(binary_path)
            elif self.config.is_common_suid(binary_name):
                standard.append(binary_path)
            else:
                unusual.append(binary_path)

        # Report exploitable binaries (CRITICAL)
        for binary_path in exploitable:
            binary_name = os.path.basename(binary_path)
            gtfobins_url = f"https://gtfobins.github.io/gtfobins/{binary_name}/#suid"

            self.log(f"EXPLOITABLE SUID: {binary_path}", "critical")
            self.log(f"  GTFOBins: {gtfobins_url}")

            self.add_finding(
                category="Exploitable SUID Binary",
                severity=FindingSeverity.CRITICAL,
                finding=f"GTFOBins SUID binary found: {binary_name}",
                exploitation=f"Check GTFOBins for exploitation:\n  {gtfobins_url}",
                impact="Critical - Direct root access possible",
                target=binary_path,
                binary_name=binary_name,
                gtfobins_url=gtfobins_url
            )

        # Report unusual binaries (HIGH - worth investigating)
        for binary_path in unusual:
            binary_name = os.path.basename(binary_path)

            # Get file info
            file_info = self._get_file_info(binary_path)

            self.log(f"Unusual SUID binary: {binary_path}", "warning")

            self.add_finding(
                category="Unusual SUID Binary",
                severity=FindingSeverity.HIGH,
                finding=f"Non-standard SUID binary: {binary_name}",
                exploitation=(
                    "Analyze binary for vulnerabilities:\n"
                    f"  strings {binary_path} | less\n"
                    f"  ltrace {binary_path}\n"
                    f"  strace {binary_path}\n"
                    "  Look for: command injection, path hijacking, buffer overflows"
                ),
                impact="High - Potential custom privilege escalation",
                target=binary_path,
                binary_name=binary_name,
                **file_info
            )

        if self.config.verbose:
            self.log(f"Standard SUID binaries (likely not exploitable): {len(standard)}")

    def _enumerate_sgid_binaries(self) -> None:
        """Find and analyze SGID binaries"""
        self.log("Searching for SGID binaries...")

        output = self.run_command(
            "find / -type f -perm -2000 2>/dev/null",
            timeout=120
        )

        if not output:
            self.log("No SGID binaries found or search failed", "warning")
            return

        sgid_binaries = [line.strip() for line in output.split('\n') if line.strip()]
        self.log(f"Found {len(sgid_binaries)} SGID binaries", "success")

        # Check for exploitable SGID binaries
        for binary_path in sgid_binaries:
            binary_name = os.path.basename(binary_path)

            if self.config.is_gtfobins(binary_name):
                gtfobins_url = f"https://gtfobins.github.io/gtfobins/{binary_name}/"

                self.log(f"Exploitable SGID: {binary_path}", "success")

                self.add_finding(
                    category="Exploitable SGID Binary",
                    severity=FindingSeverity.HIGH,
                    finding=f"GTFOBins SGID binary found: {binary_name}",
                    exploitation=f"Check GTFOBins:\n  {gtfobins_url}",
                    impact="High - Group privilege escalation possible",
                    target=binary_path,
                    binary_name=binary_name,
                    gtfobins_url=gtfobins_url
                )

    def _get_file_info(self, path: str) -> dict:
        """Get detailed file information"""
        info = {}

        try:
            stat_info = os.stat(path)
            info['owner_uid'] = stat_info.st_uid
            info['group_gid'] = stat_info.st_gid
            info['mode'] = oct(stat_info.st_mode)
            info['size'] = stat_info.st_size
        except:
            pass

        # Get file type
        file_output = self.run_command(f"file {path}")
        if file_output:
            info['file_type'] = file_output.split(':')[1].strip() if ':' in file_output else file_output

        return info