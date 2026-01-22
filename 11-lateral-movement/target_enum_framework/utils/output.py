"""
Output utilities for Target Enumeration Framework
Handles logging, console output, and formatting
"""

from enum import Enum


class OutputLevel(Enum):
    """Output message levels"""
    INFO = "[*]"
    SUCCESS = "[+]"
    FAILURE = "[-]"
    WARNING = "[!]"
    DEBUG = "[D]"


class OutputHandler:
    """Centralized output handling for consistent formatting"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def _print(self, level: OutputLevel, message: str, indent: int = 0):
        """Internal print method with formatting"""
        if not self.verbose and level == OutputLevel.DEBUG:
            return

        prefix = "    " * indent
        print(f"{prefix}{level.value} {message}")

    def info(self, message: str, indent: int = 0):
        """Print info message"""
        self._print(OutputLevel.INFO, message, indent)

    def success(self, message: str, indent: int = 0):
        """Print success message"""
        self._print(OutputLevel.SUCCESS, message, indent)

    def failure(self, message: str, indent: int = 0):
        """Print failure message"""
        self._print(OutputLevel.FAILURE, message, indent)

    def warning(self, message: str, indent: int = 0):
        """Print warning message"""
        self._print(OutputLevel.WARNING, message, indent)

    def debug(self, message: str, indent: int = 0):
        """Print debug message (only in verbose mode)"""
        self._print(OutputLevel.DEBUG, message, indent)

    def banner(self, title: str, char: str = "=", width: int = 60):
        """Print section banner"""
        print(f"\n{char * width}")
        print(title)
        print(f"{char * width}")

    def raw(self, message: str):
        """Print raw message without formatting"""
        print(message)

    def newline(self):
        """Print empty line"""
        print()

    def scan_header(self, protocol: str, network: str):
        """Print scan header"""
        self.newline()
        self.info(f"Enumerating {protocol} hosts on {network}...")

    def host_found(self, ip: str, protocol: str = None):
        """Print found host"""
        if protocol:
            self.success(f"Found {protocol}: {ip}")
        else:
            self.success(f"Found: {ip}")

    def scan_summary(self, protocol: str, count: int):
        """Print scan summary"""
        self.success(f"Found {count} {protocol} hosts")

    def stats_line(self, label: str, value: int, indent: int = 1):
        """Print statistics line"""
        prefix = "    " * indent
        print(f"{prefix}{label}: {value}")


# Global output handler instance
output = OutputHandler()