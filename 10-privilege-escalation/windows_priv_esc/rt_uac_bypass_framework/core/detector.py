import sys
import os
from typing import Dict, Optional
from dataclasses import dataclass

# Windows-specific imports
try:
    import ctypes

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


@dataclass
class WindowsInfo:
    """Windows system information."""
    major_version: int
    minor_version: int
    build_number: int
    platform_id: int
    service_pack: str
    is_64bit: bool
    edition: str


class SystemDetector:
    """Detect Windows version and system information."""

    # Windows version names
    VERSION_NAMES = {
        (10, 0): "Windows 10/11",
        (6, 3): "Windows 8.1",
        (6, 2): "Windows 8",
        (6, 1): "Windows 7",
        (6, 0): "Windows Vista",
        (5, 2): "Windows XP x64/Server 2003",
        (5, 1): "Windows XP"
    }

    # Notable build numbers
    BUILD_INFO = {
        10240: "Windows 10 1507 (RTM)",
        10586: "Windows 10 1511 (November Update)",
        14393: "Windows 10 1607 (Anniversary Update)",
        15063: "Windows 10 1703 (Creators Update)",
        16299: "Windows 10 1709 (Fall Creators Update)",
        17134: "Windows 10 1803 (April 2018 Update)",
        17763: "Windows 10 1809 (October 2018 Update)",
        18362: "Windows 10 1903 (May 2019 Update)",
        18363: "Windows 10 1909 (November 2019 Update)",
        19041: "Windows 10 2004 (May 2020 Update)",
        19042: "Windows 10 20H2",
        19043: "Windows 10 21H1",
        19044: "Windows 10 21H2",
        19045: "Windows 10 22H2",
        22000: "Windows 11 21H2",
        22621: "Windows 11 22H2",
        22631: "Windows 11 23H2"
    }

    def __init__(self):
        """Initialize the system detector."""
        self.windows_info: Optional[WindowsInfo] = None

        if WINDOWS_AVAILABLE and os.name == 'nt':
            self._detect_system()

    def _detect_system(self) -> None:
        """Detect Windows system information."""
        try:
            version = sys.getwindowsversion()

            self.windows_info = WindowsInfo(
                major_version=version.major,
                minor_version=version.minor,
                build_number=version.build,
                platform_id=version.platform,
                service_pack=version.service_pack or "",
                is_64bit=sys.maxsize > 2 ** 32,
                edition=self._get_edition()
            )
        except Exception:
            self.windows_info = None

    def _get_edition(self) -> str:
        """Get Windows edition."""
        try:
            import subprocess
            result = subprocess.run(
                'wmic os get caption',
                shell=True,
                capture_output=True,
                text=True
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].strip()
        except Exception:
            pass

        return "Unknown"

    def get_version(self) -> int:
        """Get Windows major version number."""
        if self.windows_info:
            return self.windows_info.major_version
        return 0

    def get_build(self) -> int:
        """Get Windows build number."""
        if self.windows_info:
            return self.windows_info.build_number
        return 0

    def get_version_name(self) -> str:
        """Get human-readable Windows version name."""
        if not self.windows_info:
            return "Unknown"

        key = (self.windows_info.major_version, self.windows_info.minor_version)
        base_name = self.VERSION_NAMES.get(key, "Unknown Windows")

        # Add build info if available
        build_name = self.BUILD_INFO.get(self.windows_info.build_number)

        if build_name:
            return f"{base_name} ({build_name})"
        else:
            return f"{base_name} (Build {self.windows_info.build_number})"

    def get_full_info(self) -> Dict:
        """Get complete system information."""
        if not self.windows_info:
            return {'error': 'System detection failed'}

        return {
            'major_version': self.windows_info.major_version,
            'minor_version': self.windows_info.minor_version,
            'build_number': self.windows_info.build_number,
            'service_pack': self.windows_info.service_pack,
            'is_64bit': self.windows_info.is_64bit,
            'edition': self.windows_info.edition,
            'version_name': self.get_version_name()
        }

    def print_info(self) -> None:
        """Print system information."""
        print("\n[*] Windows System Information:")

        if not self.windows_info:
            print("    Detection failed")
            return

        print(f"    Version: {self.get_version_name()}")
        print(f"    Build: {self.windows_info.build_number}")
        print(f"    Edition: {self.windows_info.edition}")
        print(f"    Architecture: {'64-bit' if self.windows_info.is_64bit else '32-bit'}")

        if self.windows_info.service_pack:
            print(f"    Service Pack: {self.windows_info.service_pack}")


if __name__ == "__main__":
    detector = SystemDetector()
    detector.print_info()