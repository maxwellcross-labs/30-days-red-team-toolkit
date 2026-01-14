import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class AIEExploitBase(ABC):
    """Abstract base class for AlwaysInstallElevated exploitation."""

    # Registry paths
    HKLM_PATH = r'SOFTWARE\Policies\Microsoft\Windows\Installer'
    HKCU_PATH = r'SOFTWARE\Policies\Microsoft\Windows\Installer'
    VALUE_NAME = 'AlwaysInstallElevated'

    def __init__(self, output_dir: str = "msi_exploits"):
        """
        Initialize the exploit base.

        Args:
            output_dir: Directory for storing output files and logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.log_file = self.output_dir / f"aie_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message to console and file.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        level_colors = {
            "INFO": "\033[94m[*]\033[0m",
            "WARNING": "\033[93m[!]\033[0m",
            "ERROR": "\033[91m[-]\033[0m",
            "SUCCESS": "\033[92m[+]\033[0m"
        }

        prefix = level_colors.get(level, "[*]")
        print(f"{prefix} {message}")

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def run_command(self, cmd: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """
        Execute a shell command safely.

        Args:
            cmd: Command to execute
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess object with stdout and stderr
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {cmd}", "ERROR")
            raise
        except Exception as e:
            self.log(f"Command failed: {cmd} - {e}", "ERROR")
            raise

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if exists, False otherwise
        """
        return os.path.exists(path)

    def get_file_size(self, path: str) -> int:
        """
        Get file size in bytes.

        Args:
            path: Path to file

        Returns:
            Size in bytes or 0 if not found
        """
        try:
            return os.path.getsize(path)
        except OSError:
            return 0