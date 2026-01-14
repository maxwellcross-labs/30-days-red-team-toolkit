import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime


class PrivilegeChecker:
    """Check and verify Windows privileges for token impersonation."""

    # Privileges required for Potato attacks
    IMPERSONATION_PRIVILEGES = [
        'SeImpersonatePrivilege',
        'SeAssignPrimaryTokenPrivilege'
    ]

    # Additional useful privileges
    USEFUL_PRIVILEGES = [
        'SeDebugPrivilege',
        'SeTcbPrivilege',
        'SeBackupPrivilege',
        'SeRestorePrivilege',
        'SeCreateTokenPrivilege',
        'SeLoadDriverPrivilege',
        'SeTakeOwnershipPrivilege'
    ]

    def __init__(self, output_dir: str = "token_impersonation"):
        """
        Initialize the privilege checker.

        Args:
            output_dir: Directory for storing output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.privileges_cache: Dict[str, bool] = {}

    def get_current_privileges(self) -> Dict[str, bool]:
        """
        Get all current user privileges and their status.

        Returns:
            Dictionary of privilege name -> enabled status
        """
        print("[*] Enumerating current privileges...")

        result = subprocess.run(
            "whoami /priv",
            shell=True,
            capture_output=True,
            text=True
        )

        privileges = {}

        for line in result.stdout.split('\n'):
            line = line.strip()

            if not line or 'PRIVILEGES INFORMATION' in line or '----' in line:
                continue

            if 'Privilege Name' in line:
                continue

            # Parse privilege line
            parts = line.split()
            if len(parts) >= 2:
                priv_name = parts[0]

                # Check if enabled
                is_enabled = 'Enabled' in line and 'Disabled' not in line
                privileges[priv_name] = is_enabled

        self.privileges_cache = privileges
        return privileges

    def check_impersonation_privileges(self) -> Tuple[bool, List[str]]:
        """
        Check if required impersonation privileges are available.

        Returns:
            Tuple of (can_impersonate, list of enabled privileges)
        """
        print("\n[*] Checking for token impersonation privileges...")

        privileges = self.get_current_privileges()

        enabled_impersonation = []

        for priv in self.IMPERSONATION_PRIVILEGES:
            if priv in privileges:
                if privileges[priv]:
                    print(f"[+] {priv}: ENABLED")
                    enabled_impersonation.append(priv)
                else:
                    print(f"[!] {priv}: DISABLED")
            else:
                print(f"[-] {priv}: NOT PRESENT")

        can_impersonate = len(enabled_impersonation) > 0

        if can_impersonate:
            print(f"\n[+] Token impersonation is POSSIBLE!")
        else:
            print(f"\n[-] No impersonation privileges found")
            print(f"[!] Potato attacks require SeImpersonate or SeAssignPrimaryToken")

        return can_impersonate, enabled_impersonation

    def check_all_useful_privileges(self) -> Dict[str, bool]:
        """
        Check all privileges useful for privilege escalation.

        Returns:
            Dictionary of useful privileges and their status
        """
        print("\n[*] Checking for useful escalation privileges...")

        privileges = self.get_current_privileges()

        useful_found = {}

        all_useful = self.IMPERSONATION_PRIVILEGES + self.USEFUL_PRIVILEGES

        for priv in all_useful:
            if priv in privileges:
                useful_found[priv] = privileges[priv]
                status = "ENABLED" if privileges[priv] else "DISABLED"
                symbol = "[+]" if privileges[priv] else "[!]"
                print(f"{symbol} {priv}: {status}")

        return useful_found

    def get_current_user_info(self) -> Dict[str, str]:
        """
        Get current user context information.

        Returns:
            Dictionary with user information
        """
        print("\n[*] Getting current user context...")

        info = {}

        # Get username
        result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
        info['username'] = result.stdout.strip()

        # Get groups
        result = subprocess.run("whoami /groups", shell=True, capture_output=True, text=True)
        info['groups_raw'] = result.stdout

        # Parse important groups
        important_groups = []
        for line in result.stdout.split('\n'):
            if any(g in line for g in ['Administrators', 'SYSTEM', 'SERVICE', 'IIS_IUSRS', 'NETWORK SERVICE']):
                important_groups.append(line.strip().split()[0] if line.strip().split() else line.strip())

        info['important_groups'] = important_groups

        # Check if service account
        is_service = any(svc in info['username'].upper() for svc in
                         ['SERVICE', 'SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE', 'IIS'])
        info['is_service_account'] = is_service

        print(f"[*] Current user: {info['username']}")
        print(f"[*] Service account: {'Yes' if is_service else 'No'}")

        if important_groups:
            print(f"[*] Notable groups: {', '.join(important_groups[:5])}")

        return info

    def export_privilege_report(self, filename: str = None) -> str:
        """
        Export a detailed privilege report.

        Args:
            filename: Optional filename

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"privilege_report_{timestamp}.txt"

        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Windows Privilege Assessment Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            # User info
            user_info = self.get_current_user_info()
            f.write(f"Current User: {user_info['username']}\n")
            f.write(f"Service Account: {user_info['is_service_account']}\n\n")

            # Privileges
            f.write("TOKEN PRIVILEGES\n")
            f.write("-" * 40 + "\n")

            privileges = self.get_current_privileges()
            for priv, enabled in sorted(privileges.items()):
                status = "ENABLED" if enabled else "DISABLED"
                f.write(f"  {priv}: {status}\n")

            # Impersonation assessment
            f.write("\nIMPERSONATION ASSESSMENT\n")
            f.write("-" * 40 + "\n")

            can_impersonate, enabled = self.check_impersonation_privileges()
            f.write(f"  Can Impersonate: {'YES' if can_impersonate else 'NO'}\n")
            f.write(f"  Enabled Privileges: {', '.join(enabled) if enabled else 'None'}\n")

        print(f"\n[+] Report exported to: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    checker = PrivilegeChecker()

    print("\n" + "=" * 60)
    print("Windows Privilege Assessment")
    print("=" * 60)

    checker.get_current_user_info()
    checker.check_impersonation_privileges()
    checker.check_all_useful_privileges()