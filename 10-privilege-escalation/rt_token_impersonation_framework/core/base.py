import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class PotatoExploitBase(ABC):
    """Abstract base class for all Potato-style token impersonation exploits."""

    # Tool download URLs
    TOOL_URLS = {
        'printspoofer': 'https://github.com/itm4n/PrintSpoofer',
        'roguepotato': 'https://github.com/antonioCoco/RoguePotato',
        'juicypotato': 'https://github.com/ohpe/juicy-potato',
        'sweetpotato': 'https://github.com/CCob/SweetPotato'
    }

    def __init__(self, tool_name: str, output_dir: str = "token_impersonation"):
        """
        Initialize the Potato exploit base.

        Args:
            tool_name: Name of the tool (printspoofer, roguepotato, etc.)
            output_dir: Directory for storing output files and logs
        """
        self.tool_name = tool_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.log_file = self.output_dir / f"{tool_name}_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Default tool path
        self.tool_path = f"C:\\Windows\\Temp\\{tool_name.capitalize()}.exe"

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

    def run_command(self, cmd: str, timeout: int = 30) -> subprocess.CompletedProcess:
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

    def check_tool_exists(self) -> bool:
        """
        Check if the exploit tool binary exists.

        Returns:
            True if tool exists, False otherwise
        """
        if os.path.exists(self.tool_path):
            self.log(f"Tool found: {self.tool_path}", "SUCCESS")
            return True
        else:
            self.log(f"Tool not found: {self.tool_path}", "ERROR")
            self.log(f"Download from: {self.TOOL_URLS.get(self.tool_name, 'Unknown')}", "INFO")
            return False

    def set_tool_path(self, path: str) -> None:
        """
        Set a custom path for the exploit tool.

        Args:
            path: Full path to the tool binary
        """
        self.tool_path = path
        self.log(f"Tool path set to: {path}", "INFO")

    def verify_system_privileges(self, output: str) -> bool:
        """
        Verify if SYSTEM privileges were obtained.

        Args:
            output: Command output to check

        Returns:
            True if SYSTEM achieved, False otherwise
        """
        system_indicators = [
            'NT AUTHORITY\\SYSTEM',
            'NT AUTHORITY/SYSTEM',
            'nt authority\\system',
            'CreateProcessWithTokenW OK',
            'CreateProcessAsUser OK'
        ]

        for indicator in system_indicators:
            if indicator.lower() in output.lower():
                return True

        return False

    @abstractmethod
    def exploit(self, command: str = "cmd.exe") -> Tuple[bool, str]:
        """
        Execute the token impersonation attack.
        Must be implemented by subclasses.

        Args:
            command: Command to execute as SYSTEM

        Returns:
            Tuple of (success, output)
        """
        pass

    @abstractmethod
    def get_requirements(self) -> dict:
        """
        Get the requirements for this exploit.
        Must be implemented by subclasses.

        Returns:
            Dictionary with requirement information
        """
        pass