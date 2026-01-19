"""
Sudo Permissions Enumerator
===========================

Enumerate sudo permissions for privilege escalation.

sudo -l reveals what commands the current user can run with elevated privileges.
NOPASSWD entries are particularly valuable as they require no authentication.
"""

import os
import re
from typing import List, Dict, Optional, Tuple

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class SudoEnumerator(BaseEnumerator):
    """
    Enumerate sudo permissions and configurations.

    Checks:
    - sudo -l output for allowed commands
    - NOPASSWD entries (highest priority)
    - Wildcards in sudo rules
    - sudo version (for exploits like CVE-2021-3156)
    """

    name = "Sudo Permissions Enumerator"
    description = "Discover sudo misconfigurations for privilege escalation"

    # Common exploitable sudo configurations
    SUDO_EXPLOITS: Dict[str, str] = {
        'env_keep': (
            'Environment variables preserved through sudo.\n'
            'Check for LD_PRELOAD, LD_LIBRARY_PATH, PYTHONPATH exploitation.'
        ),
        'wildcard': (
            'Wildcards in sudo rules can be exploited:\n'
            '  - /path/to/script * → Pass malicious arguments\n'
            '  - /path/to/* → Create symlinks to exploitable binaries'
        ),
        'relative_path': (
            'Relative paths in sudo rules enable PATH hijacking:\n'
            '  1. Create malicious script with same name\n'
            '  2. Prepend malicious directory to PATH\n'
            '  3. Execute via sudo'
        )
    }

    def enumerate(self) -> None:
        """Run sudo enumeration"""
        self.print_header()

        self._check_sudo_version()
        self._enumerate_sudo_permissions()
        self._check_sudoers_readable()

    def _check_sudo_version(self) -> None:
        """Check sudo version for known vulnerabilities"""
        self.log("Checking sudo version...")

        output = self.run_command("sudo --version 2>/dev/null | head -1")

        if output:
            self.log(f"Sudo version: {output}")

            # Extract version number
            version_match = re.search(r'(\d+\.\d+\.?\d*)', output)

            if version_match:
                version = version_match.group(1)

                # Check for CVE-2021-3156 (Baron Samedit)
                # Affects sudo < 1.9.5p2
                try:
                    major, minor = map(int, version.split('.')[:2])

                    if major == 1 and minor < 9:
                        self.log("Potentially vulnerable to CVE-2021-3156!", "critical")

                        self.add_finding(
                            category="Sudo Version Vulnerability",
                            severity=FindingSeverity.CRITICAL,
                            finding=f"Sudo version {version} may be vulnerable to Baron Samedit (CVE-2021-3156)",
                            exploitation=(
                                "Test for CVE-2021-3156:\n"
                                "  sudoedit -s '\\' $(python3 -c 'print(\"A\"*1000)')\n"
                                "  If crashes with 'malloc()' error, likely vulnerable.\n"
                                "  Exploit: https://github.com/blasty/CVE-2021-3156"
                            ),
                            impact="Critical - Heap overflow to root shell",
                            target="sudo",
                            version=version
                        )
                except ValueError:
                    pass

    def _enumerate_sudo_permissions(self) -> None:
        """Enumerate sudo -l output"""
        self.log("Checking sudo permissions (sudo -l)...")

        # Try sudo -l (may require password)
        output = self.run_command("sudo -l 2>/dev/null")

        if not output:
            # Try without TTY
            output = self.run_command("sudo -n -l 2>/dev/null")

        if not output or "not allowed" in output.lower():
            self.log("No sudo permissions or password required", "info")
            return

        if "may run the following" in output.lower():
            self.log("User has sudo permissions!", "success")
            print(output)

            self._parse_sudo_output(output)

    def _parse_sudo_output(self, output: str) -> None:
        """Parse sudo -l output for exploitable entries"""
        lines = output.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or 'may run' in line.lower():
                continue

            # Check for NOPASSWD (highest priority)
            if 'NOPASSWD' in line:
                self._handle_nopasswd_entry(line)

            # Check for environment preservation
            elif 'env_keep' in line.lower():
                self.log("Environment variables preserved!", "warning")

                self.add_finding(
                    category="Sudo Environment",
                    severity=FindingSeverity.HIGH,
                    finding="Sudo preserves environment variables",
                    exploitation=self.SUDO_EXPLOITS['env_keep'],
                    impact="High - Potential LD_PRELOAD exploitation",
                    target="sudo configuration"
                )

            # Check for command entries
            elif '/' in line and '(' in line:
                self._handle_command_entry(line)

    def _handle_nopasswd_entry(self, line: str) -> None:
        """Handle NOPASSWD sudo entries"""
        self.log(f"NOPASSWD entry found: {line}", "critical")

        # Extract command path
        commands = self._extract_commands(line)

        for command in commands:
            binary_name = os.path.basename(command.split()[0])

            # Check if it's a GTFOBins binary
            if self.config.is_gtfobins(binary_name):
                gtfobins_url = f"https://gtfobins.github.io/gtfobins/{binary_name}/#sudo"

                self.add_finding(
                    category="Sudo NOPASSWD - GTFOBins",
                    severity=FindingSeverity.CRITICAL,
                    finding=f"NOPASSWD sudo for GTFOBins binary: {binary_name}",
                    exploitation=(
                        f"Run with sudo (no password needed):\n"
                        f"  sudo {command}\n"
                        f"  GTFOBins: {gtfobins_url}"
                    ),
                    impact="Critical - Direct root shell",
                    target=command,
                    gtfobins_url=gtfobins_url
                )
            else:
                # Check for special cases
                self._check_special_sudo_commands(command, nopasswd=True)

    def _handle_command_entry(self, line: str) -> None:
        """Handle regular sudo command entries"""
        commands = self._extract_commands(line)

        for command in commands:
            if '*' in command:
                # Wildcard - potentially exploitable
                self.log(f"Wildcard sudo rule: {command}", "warning")

                self.add_finding(
                    category="Sudo Wildcard",
                    severity=FindingSeverity.HIGH,
                    finding=f"Sudo rule contains wildcard: {command}",
                    exploitation=self.SUDO_EXPLOITS['wildcard'],
                    impact="High - Argument injection possible",
                    target=command
                )
            else:
                self._check_special_sudo_commands(command, nopasswd=False)

    def _extract_commands(self, line: str) -> List[str]:
        """Extract command paths from sudo output line"""
        commands = []

        # Handle format: (root) NOPASSWD: /bin/command, /bin/other
        # or (ALL : ALL) /bin/command

        # Remove user/group specifier
        if ')' in line:
            line = line.split(')', 1)[1]

        # Remove NOPASSWD/PASSWD
        line = re.sub(r'NOPASSWD:|PASSWD:', '', line)

        # Split on comma and clean up
        parts = line.split(',')

        for part in parts:
            part = part.strip()
            if part.startswith('/') or part == 'ALL':
                commands.append(part)

        return commands

    def _check_special_sudo_commands(self, command: str, nopasswd: bool) -> None:
        """Check for special sudo command misconfigurations"""
        command_lower = command.lower()
        severity = FindingSeverity.CRITICAL if nopasswd else FindingSeverity.HIGH

        special_checks = [
            # Command contains ALL
            (command == 'ALL',
             "Full sudo access",
             "User can run any command as root:\n  sudo su -"),

            # Text editors (vim, nano, etc.)
            (any(ed in command_lower for ed in ['vim', 'vi', 'nano', 'emacs']),
             "Text editor with sudo",
             "Spawn shell from editor:\n  vim → :!/bin/bash"),

            # Package managers
            (any(pkg in command_lower for pkg in ['apt', 'yum', 'dnf', 'pip']),
             "Package manager with sudo",
             "Install malicious package or use hooks for code execution"),

            # Script interpreters
            (any(lang in command_lower for lang in ['python', 'perl', 'ruby', 'php']),
             "Script interpreter with sudo",
             "Execute shell:\n  python -c 'import os; os.system(\"/bin/bash\")'"),

            # File operations
            ('cp' in command_lower or 'mv' in command_lower,
             "File copy/move with sudo",
             "Overwrite /etc/passwd or /etc/shadow"),

            # Tar/archive
            ('tar' in command_lower,
             "Tar with sudo",
             "Use checkpoint action:\n  sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash"),
        ]

        for condition, category, exploitation in special_checks:
            if condition:
                self.add_finding(
                    category=f"Sudo Misconfiguration - {category}",
                    severity=severity,
                    finding=f"{'NOPASSWD ' if nopasswd else ''}sudo for: {command}",
                    exploitation=exploitation,
                    impact="Critical - Root shell achievable" if nopasswd else "High - Root access possible",
                    target=command,
                    nopasswd=nopasswd
                )
                break

    def _check_sudoers_readable(self) -> None:
        """Check if sudoers file is readable"""
        self.log("Checking sudoers file accessibility...")

        sudoers_paths = [
            '/etc/sudoers',
            '/etc/sudoers.d/'
        ]

        for path in sudoers_paths:
            if os.path.exists(path) and os.access(path, os.R_OK):
                self.log(f"Readable: {path}", "warning")

                self.add_finding(
                    category="Sudoers File Readable",
                    severity=FindingSeverity.LOW,
                    finding=f"Sudoers configuration readable: {path}",
                    exploitation="Read for additional sudo rules and attack surface",
                    impact="Low - Information disclosure",
                    target=path
                )