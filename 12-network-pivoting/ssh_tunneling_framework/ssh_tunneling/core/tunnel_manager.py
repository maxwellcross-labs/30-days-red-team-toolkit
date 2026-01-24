"""
Tunnel Manager
Main manager class for SSH tunnels
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime

from .base_tunnel import BaseTunnel


class TunnelManager:
    """Manager for SSH tunnels"""

    def __init__(self, output_dir: str = "ssh_tunnels"):
        """
        Initialize tunnel manager

        Args:
            output_dir: Output directory for logs and configs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.active_tunnels: List[BaseTunnel] = []

        print(f"[+] SSH Tunneling Framework initialized")
        print(f"[+] Output directory: {self.output_dir}")

    def add_tunnel(self, tunnel: BaseTunnel) -> bool:
        """
        Add and establish a tunnel

        Args:
            tunnel: BaseTunnel instance

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Establishing tunnel: {tunnel.__class__.__name__}")

        if tunnel.establish():
            self.active_tunnels.append(tunnel)
            self._log_tunnel(tunnel)
            return True

        return False

    def _log_tunnel(self, tunnel: BaseTunnel):
        """
        Log tunnel information

        Args:
            tunnel: BaseTunnel instance
        """
        log_file = self.output_dir / "tunnel_log.txt"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(str(tunnel))

    def list_active_tunnels(self):
        """List all active SSH tunnels"""
        print(f"\n" + "=" * 60)
        print(f"ACTIVE SSH TUNNELS")
        print(f"=" * 60)

        if not self.active_tunnels:
            print(f"\n[*] No active tunnels")
            return

        for i, tunnel in enumerate(self.active_tunnels, 1):
            print(f"\n[{i}] {tunnel.__class__.__name__}")

            info = tunnel.get_info()
            for key, value in info.items():
                print(f"    {key}: {value}")

    def get_tunnel_count(self) -> int:
        """
        Get number of active tunnels

        Returns:
            Number of active tunnels
        """
        return len(self.active_tunnels)

    def get_output_dir(self) -> Path:
        """
        Get output directory path

        Returns:
            Output directory Path object
        """
        return self.output_dir