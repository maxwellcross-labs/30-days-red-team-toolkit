"""
Bypass Selector Module
Automatically selects the best UAC bypass method for the current system.
"""

from typing import List, Optional, Dict
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))

from ..core.detector import SystemDetector
from ..core.uac_checker import UACChecker
from ..bypasses import BYPASS_METHODS


class BypassSelector:
    """Select the best UAC bypass method for the current system."""

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the bypass selector.

        Args:
            output_dir: Directory for output files
            verbose: Enable verbose logging
        """
        self.output_dir = output_dir
        self.verbose = verbose

        self.detector = SystemDetector()
        self.checker = UACChecker()

        self.windows_version = self.detector.get_version()
        self.windows_build = self.detector.get_build()

    def get_compatible_methods(self) -> List[Dict]:
        """
        Get all compatible bypass methods for current system.

        Returns:
            List of compatible method information dictionaries
        """
        compatible = []

        for name, bypass_class in BYPASS_METHODS.items():
            # Create temporary instance to check compatibility
            bypass = bypass_class(self.output_dir, self.verbose)

            if bypass.is_compatible(self.windows_version, self.windows_build):
                info = bypass.get_info()
                info['class'] = bypass_class
                compatible.append(info)

        return compatible

    def select_best_method(self) -> Optional[str]:
        """
        Select the best bypass method based on success rate and detection risk.

        Returns:
            Method name or None if no compatible methods
        """
        compatible = self.get_compatible_methods()

        if not compatible:
            return None

        # Sort by success rate (descending)
        compatible.sort(key=lambda x: x['success_rate'], reverse=True)

        return compatible[0]['name']

    def enumerate_methods(self) -> None:
        """Display all compatible methods."""
        print("\n" + "=" * 60)
        print("COMPATIBLE UAC BYPASS METHODS")
        print("=" * 60)

        # Check prerequisites
        can_bypass, reason = self.checker.can_bypass_uac()

        print(f"\nCurrent Status:")
        print(f"  Administrator: {'Yes' if self.checker.is_admin() else 'No'}")
        print(f"  UAC Enabled: {'Yes' if self.checker.is_uac_enabled() else 'No'}")
        print(f"  Can Bypass: {'Yes' if can_bypass else 'No'} ({reason})")

        if not can_bypass:
            return

        compatible = self.get_compatible_methods()

        if not compatible:
            print("\n[-] No compatible bypass methods found")
            print(f"[*] Windows {self.windows_version} build {self.windows_build} may be fully patched")
            return

        print(f"\nCompatible Methods ({len(compatible)}):")
        print("-" * 60)

        for i, method in enumerate(compatible, 1):
            print(f"\n[{i}] {method['name'].upper()}")
            print(f"    Description: {method['description']}")
            print(f"    Detection Risk: {method['detection_risk']}")
            print(f"    Success Rate: {method['success_rate'] * 100:.0f}%")

        # Show recommendation
        best = self.select_best_method()
        if best:
            print(f"\n[+] Recommended method: {best}")

    def get_bypass_instance(self, method_name: str):
        """
        Get a bypass instance for the specified method.

        Args:
            method_name: Name of the bypass method

        Returns:
            Bypass instance or None
        """
        if method_name == 'auto':
            method_name = self.select_best_method()
            if not method_name:
                return None

        if method_name not in BYPASS_METHODS:
            return None

        return BYPASS_METHODS[method_name](self.output_dir, self.verbose)


if __name__ == "__main__":
    selector = BypassSelector(verbose=True)
    selector.enumerate_methods()