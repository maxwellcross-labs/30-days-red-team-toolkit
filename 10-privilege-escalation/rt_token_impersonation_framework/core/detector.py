import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SystemInfo:
    """Windows system information container."""
    os_name: str
    os_version: str
    build_number: int
    architecture: str
    is_server: bool
    recommended_tools: List[str]


class SystemDetector:
    """Detect Windows version and recommend appropriate attack tools."""

    # Tool compatibility matrix
    TOOL_COMPATIBILITY = {
        'printspoofer': {
            'min_build': 17763,  # Windows 10 1809+
            'works_on': ['Windows 10', 'Windows 11', 'Server 2019', 'Server 2022'],
            'description': 'Abuses SpoolSS to impersonate SYSTEM'
        },
        'roguepotato': {
            'min_build': 17763,
            'works_on': ['Windows 10', 'Windows 11', 'Server 2019', 'Server 2022'],
            'description': 'Remote Potato variant, requires relay server'
        },
        'juicypotato': {
            'max_build': 17763,  # Patched in 1809
            'works_on': ['Server 2008', 'Server 2012', 'Server 2016', 'Windows 7', 'Windows 8'],
            'description': 'BITS-based DCOM impersonation'
        },
        'sweetpotato': {
            'min_build': 0,  # Works on most versions
            'works_on': ['Windows 10', 'Windows 11', 'Server 2016', 'Server 2019', 'Server 2022'],
            'description': 'Collection of Potato techniques'
        }
    }

    def __init__(self):
        """Initialize the system detector."""
        self.system_info: Optional[SystemInfo] = None

    def detect_system(self) -> SystemInfo:
        """
        Detect the current Windows system version.

        Returns:
            SystemInfo object with system details
        """
        print("[*] Detecting Windows version...")

        # Get OS information
        cmd = 'systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        os_name = ""
        os_version = ""
        architecture = ""

        for line in result.stdout.split('\n'):
            if 'OS Name:' in line:
                os_name = line.split(':', 1)[1].strip()
            elif 'OS Version:' in line:
                os_version = line.split(':', 1)[1].strip()
            elif 'System Type:' in line:
                arch_str = line.split(':', 1)[1].strip()
                architecture = '64-bit' if 'x64' in arch_str else '32-bit'

        # Extract build number
        build_number = self._extract_build_number(os_version)

        # Check if server
        is_server = 'Server' in os_name

        # Determine recommended tools
        recommended = self._get_recommended_tools(os_name, build_number)

        self.system_info = SystemInfo(
            os_name=os_name,
            os_version=os_version,
            build_number=build_number,
            architecture=architecture,
            is_server=is_server,
            recommended_tools=recommended
        )

        print(f"[+] OS: {os_name}")
        print(f"[+] Version: {os_version}")
        print(f"[+] Build: {build_number}")
        print(f"[+] Architecture: {architecture}")
        print(f"[+] Server: {'Yes' if is_server else 'No'}")

        return self.system_info

    def _extract_build_number(self, version_string: str) -> int:
        """
        Extract the build number from version string.

        Args:
            version_string: OS version string

        Returns:
            Build number as integer
        """
        try:
            # Version format: 10.0.19041 N/A Build 19041
            parts = version_string.split()

            for i, part in enumerate(parts):
                if part == 'Build':
                    return int(parts[i + 1])

                # Try direct version number
                if '.' in part:
                    version_parts = part.split('.')
                    if len(version_parts) >= 3:
                        return int(version_parts[2])

            return 0
        except (ValueError, IndexError):
            return 0

    def _get_recommended_tools(self, os_name: str, build_number: int) -> List[str]:
        """
        Get recommended tools based on OS version.

        Args:
            os_name: Operating system name
            build_number: Windows build number

        Returns:
            List of recommended tool names in priority order
        """
        recommended = []

        # Check Windows 10 1809+ / Server 2019+
        if build_number >= 17763:
            # JuicyPotato doesn't work
            recommended = ['printspoofer', 'roguepotato', 'sweetpotato']

        # Older Windows 10 / Server 2016
        elif 'Server 2016' in os_name or (build_number > 0 and build_number < 17763):
            recommended = ['juicypotato', 'sweetpotato', 'printspoofer']

        # Server 2012 / 2008
        elif 'Server 2012' in os_name or 'Server 2008' in os_name:
            recommended = ['juicypotato']

        # Default fallback
        else:
            recommended = ['printspoofer', 'roguepotato', 'juicypotato', 'sweetpotato']

        return recommended

    def get_tool_info(self, tool_name: str) -> Dict:
        """
        Get detailed information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool information
        """
        return self.TOOL_COMPATIBILITY.get(tool_name, {})

    def print_recommendations(self) -> None:
        """Print detailed recommendations for the current system."""
        if not self.system_info:
            self.detect_system()

        print(f"\n" + "=" * 60)
        print("TOOL RECOMMENDATIONS")
        print("=" * 60)

        for i, tool in enumerate(self.system_info.recommended_tools, 1):
            info = self.get_tool_info(tool)

            print(f"\n[{i}] {tool.upper()}")
            print(f"    Description: {info.get('description', 'N/A')}")
            print(f"    Compatible: {', '.join(info.get('works_on', []))}")

        print(f"\n[*] Recommended order: {' -> '.join(self.system_info.recommended_tools)}")

        # Special notes
        if self.system_info.build_number >= 17763:
            print(f"\n[!] Note: JuicyPotato is PATCHED on this system (Build {self.system_info.build_number})")
            print(f"[*] Use PrintSpoofer or RoguePotato instead")

    def is_tool_compatible(self, tool_name: str) -> bool:
        """
        Check if a specific tool is compatible with current system.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if compatible, False otherwise
        """
        if not self.system_info:
            self.detect_system()

        return tool_name in self.system_info.recommended_tools


if __name__ == "__main__":
    detector = SystemDetector()

    print("\n" + "=" * 60)
    print("Windows System Detection")
    print("=" * 60 + "\n")

    detector.detect_system()
    detector.print_recommendations()