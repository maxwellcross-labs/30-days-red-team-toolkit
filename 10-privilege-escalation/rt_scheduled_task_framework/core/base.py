import os
import subprocess
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class TaskExploitBase(ABC):
    """Abstract base class for scheduled task exploitation."""

    def __init__(self, output_dir: str = "task_exploits", verbose: bool = False):
        """
        Initialize the exploit base.

        Args:
            output_dir: Directory for storing output files and backups
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.backup_dir = self.output_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.verbose = verbose
        self.log_file = self.output_dir / f"task_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

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

    def execute_command(self, cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a shell command safely.

        Args:
            cmd: Command to execute
            timeout: Command timeout in seconds

        Returns:
            Dictionary with success, stdout, stderr, returncode
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {cmd}", "ERROR")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def backup_file(self, file_path: str) -> Optional[Path]:
        """
        Create a timestamped backup of a file.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file or None on failure
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = self.backup_dir / f"{filename}.{timestamp}.backup"

            shutil.copy2(file_path, backup_path)

            if self.verbose:
                self.log(f"Backup created: {backup_path}", "INFO")

            return backup_path
        except Exception as e:
            self.log(f"Backup failed: {e}", "ERROR")
            return None

    def restore_file(self, target_path: str, backup_path: Path) -> bool:
        """
        Restore a file from backup.

        Args:
            target_path: Path to restore to
            backup_path: Path to backup file

        Returns:
            True if successful, False otherwise
        """
        try:
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            self.log(f"Restore failed: {e}", "ERROR")
            return False

    def preserve_timestamps(self, target_file: str, reference_file: str) -> bool:
        """
        Copy timestamps from reference file to target file.

        Args:
            target_file: File to update timestamps on
            reference_file: File to copy timestamps from

        Returns:
            True if successful, False otherwise
        """
        try:
            stat_info = os.stat(reference_file)
            os.utime(target_file, (stat_info.st_atime, stat_info.st_mtime))
            return True
        except Exception as e:
            if self.verbose:
                self.log(f"Failed to preserve timestamps: {e}", "WARNING")
            return False

    def is_writable(self, path: str) -> bool:
        """
        Check if current user can write to file or directory.

        Args:
            path: Path to check

        Returns:
            True if writable, False otherwise
        """
        try:
            result = self.execute_command(f'icacls "{path}"')

            if not result['success']:
                return False

            output = result['stdout']
            write_perms = ['(F)', '(M)', '(W)']
            current_user = os.environ.get('USERNAME', '').upper()

            for line in output.split('\n'):
                line_upper = line.upper()

                if current_user in line_upper or 'EVERYONE' in line_upper or 'USERS' in line_upper:
                    if any(perm in line for perm in write_perms):
                        return True

            return False
        except Exception:
            return False