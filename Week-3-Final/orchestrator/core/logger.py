"""
Operation Logger
================

Centralized logging for the attack operation.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json


class OperationLogger:
    """
    Handles logging for the attack operation.

    Supports:
    - Console output with timestamps
    - File logging
    - Structured JSON logging
    """

    def __init__(self, output_dir: Path, log_file: str = "operation.log"):
        """
        Initialize the logger.

        Args:
            output_dir: Directory for log files
            log_file: Name of the main log file
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.log_file = self.output_dir / log_file
        self.json_log_file = self.output_dir / "operation.json"

        self.entries: List[dict] = []
        self.console_enabled = True
        self.file_enabled = True

        # Initialize log files
        self._init_log_files()

    def _init_log_files(self) -> None:
        """Initialize log files with headers"""
        with open(self.log_file, "w") as f:
            f.write(f"# Operation Log - Started {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message.

        Args:
            message: The message to log
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now()
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Create log entry
        entry = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": message,
        }
        self.entries.append(entry)

        # Format for display
        log_line = f"[{formatted_time}] [{level}] {message}"

        # Console output
        if self.console_enabled:
            # Add color codes for terminal
            colors = {
                "INFO": "",
                "WARNING": "\033[93m",  # Yellow
                "ERROR": "\033[91m",  # Red
                "SUCCESS": "\033[92m",  # Green
            }
            reset = "\033[0m"
            color = colors.get(level, "")
            print(f"{color}{log_line}{reset if color else ''}")

        # File output
        if self.file_enabled:
            with open(self.log_file, "a") as f:
                f.write(log_line + "\n")

    def info(self, message: str) -> None:
        """Log an info message"""
        self.log(message, "INFO")

    def warning(self, message: str) -> None:
        """Log a warning message"""
        self.log(message, "WARNING")

    def error(self, message: str) -> None:
        """Log an error message"""
        self.log(message, "ERROR")

    def success(self, message: str) -> None:
        """Log a success message"""
        self.log(message, "SUCCESS")

    def header(self, text: str) -> None:
        """Log a section header"""
        self.log("=" * 60)
        self.log(text)
        self.log("=" * 60)

    def section(self, text: str) -> None:
        """Log a subsection"""
        self.log(f"\n[*] {text}")

    def bullet(self, text: str, indent: int = 1) -> None:
        """Log a bullet point"""
        prefix = "    " * indent
        self.log(f"{prefix}- {text}")

    def save_json_log(self) -> None:
        """Save the complete log as JSON"""
        with open(self.json_log_file, "w") as f:
            json.dump(self.entries, f, indent=2)

    def get_entries_by_level(self, level: str) -> List[dict]:
        """Get all log entries of a specific level"""
        return [e for e in self.entries if e["level"] == level]

    def get_errors(self) -> List[dict]:
        """Get all error entries"""
        return self.get_entries_by_level("ERROR")

    def get_warnings(self) -> List[dict]:
        """Get all warning entries"""
        return self.get_entries_by_level("WARNING")

    def __call__(self, message: str, level: str = "INFO") -> None:
        """Allow logger to be called directly"""
        self.log(message, level)