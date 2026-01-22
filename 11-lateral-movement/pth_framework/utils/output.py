"""
Output utilities for Pass-the-Hash Framework
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

    def target_header(self, target: str, username: str, domain: str = "."):
        """Print target authentication header"""
        self.info(f"Target: {target}")
        self.info(f"User: {domain}\\{username}")

    def command_display(self, command: str):
        """Display command being executed"""
        self.info(f"Command: {command}")

    def output_display(self, output: str, title: str = "Output"):
        """Display command output"""
        self.info(f"{title}:")
        print(output)


# Global output handler instance
output = OutputHandler()