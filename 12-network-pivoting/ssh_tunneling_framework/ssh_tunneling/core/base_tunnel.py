"""
Base Tunnel Class
Abstract base class for all SSH tunnel types
"""

from abc import ABC, abstractmethod
import subprocess
from pathlib import Path
from typing import Dict, Optional, List


class BaseTunnel(ABC):
    """Abstract base class for SSH tunnels"""

    def __init__(self, pivot_host: str, pivot_user: str, pivot_key: str):
        """
        Initialize base tunnel

        Args:
            pivot_host: Pivot host IP/hostname
            pivot_user: SSH username for pivot
            pivot_key: Path to SSH private key
        """
        self.pivot_host = pivot_host
        self.pivot_user = pivot_user
        self.pivot_key = pivot_key

        self.tunnel_info: Dict = {}
        self.is_active = False

    @abstractmethod
    def establish(self) -> bool:
        """
        Establish the tunnel

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_usage_info(self) -> str:
        """
        Get usage information for this tunnel

        Returns:
            Usage information string
        """
        pass

    def _execute_ssh_command(self, cmd: List[str], timeout: int = 5) -> bool:
        """
        Execute SSH command

        Args:
            cmd: SSH command as list
            timeout: Command timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        print(f"[*] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0 or 'background' in result.stderr.lower():
                return True
            else:
                print(f"\n[-] Command failed")
                print(f"[*] Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            # Timeout is expected for background processes
            print(f"\n[+] Command likely successful (backgrounded)")
            return True

        except Exception as e:
            print(f"\n[-] Error executing command: {e}")
            return False

    def get_info(self) -> Dict:
        """
        Get tunnel information

        Returns:
            Dictionary containing tunnel information
        """
        return self.tunnel_info

    def __str__(self) -> str:
        """String representation of tunnel"""
        info_str = f"Tunnel Type: {self.__class__.__name__}\n"
        for key, value in self.tunnel_info.items():
            info_str += f"  {key}: {value}\n"
        return info_str