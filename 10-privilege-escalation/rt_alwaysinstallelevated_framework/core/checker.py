import subprocess
from typing import Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime

# Try to import winreg (Windows only)
try:
    import winreg

    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False


class RegistryChecker:
    """Check for AlwaysInstallElevated registry misconfiguration."""

    # Registry paths
    HKLM_PATH = r'SOFTWARE\Policies\Microsoft\Windows\Installer'
    HKCU_PATH = r'SOFTWARE\Policies\Microsoft\Windows\Installer'
    VALUE_NAME = 'AlwaysInstallElevated'

    def __init__(self, output_dir: str = "msi_exploits"):
        """
        Initialize the registry checker.

        Args:
            output_dir: Directory for storing output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.hklm_enabled = False
        self.hkcu_enabled = False

    def check_hklm(self) -> Tuple[bool, str]:
        """
        Check HKEY_LOCAL_MACHINE for AlwaysInstallElevated.

        Returns:
            Tuple of (is_enabled, status_message)
        """
        if WINREG_AVAILABLE:
            return self._check_hklm_winreg()
        else:
            return self._check_hklm_reg_query()

    def _check_hklm_winreg(self) -> Tuple[bool, str]:
        """Check HKLM using winreg module."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.HKLM_PATH,
                0,
                winreg.KEY_READ
            )

            value, _ = winreg.QueryValueEx(key, self.VALUE_NAME)
            winreg.CloseKey(key)

            if value == 1:
                self.hklm_enabled = True
                return True, f"HKLM\\{self.HKLM_PATH}\\{self.VALUE_NAME} = 1 (ENABLED)"
            else:
                return False, f"HKLM\\{self.HKLM_PATH}\\{self.VALUE_NAME} = {value} (NOT 1)"

        except FileNotFoundError:
            return False, "HKLM key not found"
        except PermissionError:
            return False, "HKLM access denied"
        except Exception as e:
            return False, f"HKLM error: {e}"

    def _check_hklm_reg_query(self) -> Tuple[bool, str]:
        """Check HKLM using reg query command (fallback)."""
        cmd = f'reg query "HKLM\\{self.HKLM_PATH}" /v {self.VALUE_NAME}'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and '0x1' in result.stdout:
            self.hklm_enabled = True
            return True, f"HKLM\\{self.HKLM_PATH}\\{self.VALUE_NAME} = 1 (ENABLED)"
        elif result.returncode == 0:
            return False, f"HKLM key exists but not set to 1"
        else:
            return False, "HKLM key not found"

    def check_hkcu(self) -> Tuple[bool, str]:
        """
        Check HKEY_CURRENT_USER for AlwaysInstallElevated.

        Returns:
            Tuple of (is_enabled, status_message)
        """
        if WINREG_AVAILABLE:
            return self._check_hkcu_winreg()
        else:
            return self._check_hkcu_reg_query()

    def _check_hkcu_winreg(self) -> Tuple[bool, str]:
        """Check HKCU using winreg module."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.HKCU_PATH,
                0,
                winreg.KEY_READ
            )

            value, _ = winreg.QueryValueEx(key, self.VALUE_NAME)
            winreg.CloseKey(key)

            if value == 1:
                self.hkcu_enabled = True
                return True, f"HKCU\\{self.HKCU_PATH}\\{self.VALUE_NAME} = 1 (ENABLED)"
            else:
                return False, f"HKCU\\{self.HKCU_PATH}\\{self.VALUE_NAME} = {value} (NOT 1)"

        except FileNotFoundError:
            return False, "HKCU key not found"
        except PermissionError:
            return False, "HKCU access denied"
        except Exception as e:
            return False, f"HKCU error: {e}"

    def _check_hkcu_reg_query(self) -> Tuple[bool, str]:
        """Check HKCU using reg query command (fallback)."""
        cmd = f'reg query "HKCU\\{self.HKCU_PATH}" /v {self.VALUE_NAME}'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and '0x1' in result.stdout:
            self.hkcu_enabled = True
            return True, f"HKCU\\{self.HKCU_PATH}\\{self.VALUE_NAME} = 1 (ENABLED)"
        elif result.returncode == 0:
            return False, f"HKCU key exists but not set to 1"
        else:
            return False, "HKCU key not found"

    def is_vulnerable(self) -> bool:
        """
        Check if system is vulnerable to AlwaysInstallElevated.
        Both HKLM and HKCU must be set to 1.

        Returns:
            True if vulnerable, False otherwise
        """
        print("\n[*] Checking AlwaysInstallElevated registry keys...")

        hklm_result, hklm_msg = self.check_hklm()
        hkcu_result, hkcu_msg = self.check_hkcu()

        # Display results
        symbol_hklm = "[+]" if hklm_result else "[-]"
        symbol_hkcu = "[+]" if hkcu_result else "[-]"

        print(f"{symbol_hklm} {hklm_msg}")
        print(f"{symbol_hkcu} {hkcu_msg}")

        if hklm_result and hkcu_result:
            print(f"\n[+] AlwaysInstallElevated is ENABLED!")
            print(f"[+] MSI packages will install with SYSTEM privileges")
            return True
        else:
            print(f"\n[-] AlwaysInstallElevated is NOT fully enabled")
            print(f"[*] Both HKLM and HKCU must be set to 1")
            return False

    def get_status(self) -> Dict[str, any]:
        """
        Get detailed status of AlwaysInstallElevated configuration.

        Returns:
            Dictionary with status information
        """
        hklm_result, hklm_msg = self.check_hklm()
        hkcu_result, hkcu_msg = self.check_hkcu()

        return {
            'vulnerable': hklm_result and hkcu_result,
            'hklm': {
                'enabled': hklm_result,
                'message': hklm_msg,
                'path': f'HKLM\\{self.HKLM_PATH}\\{self.VALUE_NAME}'
            },
            'hkcu': {
                'enabled': hkcu_result,
                'message': hkcu_msg,
                'path': f'HKCU\\{self.HKCU_PATH}\\{self.VALUE_NAME}'
            }
        }

    def export_report(self, filename: str = None) -> str:
        """
        Export a vulnerability assessment report.

        Args:
            filename: Optional filename

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"aie_check_{timestamp}.txt"

        filepath = self.output_dir / filename
        status = self.get_status()

        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("AlwaysInstallElevated Vulnerability Assessment\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"VULNERABLE: {'YES' if status['vulnerable'] else 'NO'}\n\n")

            f.write("Registry Keys:\n")
            f.write("-" * 40 + "\n")
            f.write(f"  HKLM: {status['hklm']['path']}\n")
            f.write(f"    Status: {'ENABLED' if status['hklm']['enabled'] else 'NOT ENABLED'}\n")
            f.write(f"    Detail: {status['hklm']['message']}\n\n")

            f.write(f"  HKCU: {status['hkcu']['path']}\n")
            f.write(f"    Status: {'ENABLED' if status['hkcu']['enabled'] else 'NOT ENABLED'}\n")
            f.write(f"    Detail: {status['hkcu']['message']}\n\n")

            if status['vulnerable']:
                f.write("EXPLOITATION:\n")
                f.write("-" * 40 + "\n")
                f.write("  This system is vulnerable to AlwaysInstallElevated exploitation.\n")
                f.write("  A malicious MSI package can be installed with SYSTEM privileges.\n")

        print(f"\n[+] Report exported to: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    checker = RegistryChecker()

    print("\n" + "=" * 60)
    print("AlwaysInstallElevated Vulnerability Check")
    print("=" * 60)

    if checker.is_vulnerable():
        print("\n[!] System is VULNERABLE - exploitation possible")
    else:
        print("\n[*] System is NOT vulnerable")