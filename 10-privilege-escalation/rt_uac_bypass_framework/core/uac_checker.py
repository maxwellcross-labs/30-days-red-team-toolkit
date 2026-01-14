import os
from typing import Dict, Tuple

# Windows-specific imports
try:
    import winreg
    import ctypes

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class UACChecker:
    """Check UAC status and admin privileges."""

    # UAC registry path
    UAC_REG_PATH = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'

    # UAC levels
    UAC_LEVELS = {
        0: "Never notify",
        1: "Notify only for programs",
        2: "Default (notify for programs, dim desktop)",
        3: "Always notify, dim desktop"
    }

    def __init__(self):
        """Initialize the UAC checker."""
        self._is_admin = None
        self._uac_enabled = None
        self._uac_level = None

    def is_admin(self) -> bool:
        """
        Check if running with administrator privileges.

        Returns:
            True if admin, False otherwise
        """
        if self._is_admin is not None:
            return self._is_admin

        try:
            if WINDOWS_AVAILABLE:
                self._is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                self._is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        except Exception:
            self._is_admin = False

        return self._is_admin

    def is_uac_enabled(self) -> bool:
        """
        Check if UAC is enabled.

        Returns:
            True if UAC enabled, False otherwise
        """
        if self._uac_enabled is not None:
            return self._uac_enabled

        if not WINDOWS_AVAILABLE:
            return True  # Assume enabled

        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.UAC_REG_PATH,
                0,
                winreg.KEY_READ
            )

            value, _ = winreg.QueryValueEx(key, 'EnableLUA')
            winreg.CloseKey(key)

            self._uac_enabled = value == 1
        except Exception:
            self._uac_enabled = True  # Assume enabled if can't check

        return self._uac_enabled

    def get_uac_level(self) -> int:
        """
        Get the current UAC notification level.

        Returns:
            UAC level (0-3)
        """
        if self._uac_level is not None:
            return self._uac_level

        if not WINDOWS_AVAILABLE:
            return 2  # Default

        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.UAC_REG_PATH,
                0,
                winreg.KEY_READ
            )

            consent_admin, _ = winreg.QueryValueEx(key, 'ConsentPromptBehaviorAdmin')
            prompt_secure, _ = winreg.QueryValueEx(key, 'PromptOnSecureDesktop')

            winreg.CloseKey(key)

            # Determine level based on values
            if consent_admin == 0:
                self._uac_level = 0  # Never notify
            elif consent_admin == 5 and prompt_secure == 0:
                self._uac_level = 1  # Notify, no dim
            elif consent_admin == 5 and prompt_secure == 1:
                self._uac_level = 2  # Default
            elif consent_admin == 2:
                self._uac_level = 3  # Always notify
            else:
                self._uac_level = 2  # Default

        except Exception:
            self._uac_level = 2  # Default

        return self._uac_level

    def get_uac_level_name(self) -> str:
        """Get human-readable UAC level name."""
        level = self.get_uac_level()
        return self.UAC_LEVELS.get(level, "Unknown")

    def can_bypass_uac(self) -> Tuple[bool, str]:
        """
        Check if UAC bypass is possible/needed.

        Returns:
            Tuple of (can_bypass, reason)
        """
        if not self.is_admin():
            return False, "Not running as administrator"

        if not self.is_uac_enabled():
            return False, "UAC is disabled (bypass not needed)"

        return True, "UAC bypass is possible"

    def get_status(self) -> Dict:
        """Get complete UAC status."""
        return {
            'is_admin': self.is_admin(),
            'uac_enabled': self.is_uac_enabled(),
            'uac_level': self.get_uac_level(),
            'uac_level_name': self.get_uac_level_name(),
            'can_bypass': self.can_bypass_uac()[0],
            'bypass_reason': self.can_bypass_uac()[1]
        }

    def print_status(self) -> None:
        """Print UAC status."""
        print("\n[*] UAC Status:")
        print(f"    Administrator: {'Yes' if self.is_admin() else 'No'}")
        print(f"    UAC Enabled: {'Yes' if self.is_uac_enabled() else 'No'}")
        print(f"    UAC Level: {self.get_uac_level()} - {self.get_uac_level_name()}")

        can_bypass, reason = self.can_bypass_uac()
        print(f"    Can Bypass: {'Yes' if can_bypass else 'No'} ({reason})")


if __name__ == "__main__":
    checker = UACChecker()
    checker.print_status()