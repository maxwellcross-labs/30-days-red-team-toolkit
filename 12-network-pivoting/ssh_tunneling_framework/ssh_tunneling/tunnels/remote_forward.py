"""
Remote Port Forward Tunnel
Forward port on pivot back to attacker machine
"""

from typing import List

from ..core.base_tunnel import BaseTunnel


class RemoteForwardTunnel(BaseTunnel):
    """Remote port forwarding (SSH -R)"""

    def __init__(
            self,
            pivot_host: str,
            pivot_user: str,
            pivot_key: str,
            attacker_port: int,
            remote_port: int
    ):
        """
        Initialize remote port forward tunnel

        Args:
            pivot_host: Pivot host IP/hostname
            pivot_user: SSH username for pivot
            pivot_key: Path to SSH private key
            attacker_port: Port on attacker machine
            remote_port: Port on pivot to bind
        """
        super().__init__(pivot_host, pivot_user, pivot_key)

        self.attacker_port = attacker_port
        self.remote_port = remote_port

        self.tunnel_info = {
            'type': 'remote_forward',
            'pivot': f'{pivot_user}@{pivot_host}',
            'attacker_port': attacker_port,
            'remote_port': remote_port
        }

    def establish(self) -> bool:
        """
        Establish remote port forward

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Setting up REMOTE port forward...")
        print(f"[*] Pivot: {self.pivot_user}@{self.pivot_host}")
        print(f"[*] Target port (on attacker): {self.attacker_port}")
        print(f"[*] Remote port (on pivot): {self.remote_port}")

        # SSH command: -R remote_port:localhost:attacker_port
        cmd = [
            'ssh',
            '-i', self.pivot_key,
            '-R', f'{self.remote_port}:localhost:{self.attacker_port}',
            '-N',  # Don't execute remote command
            '-f',  # Background
            f'{self.pivot_user}@{self.pivot_host}'
        ]

        if self._execute_ssh_command(cmd):
            self.is_active = True
            print(f"\n[+] Remote port forward established!")
            print(f"[+] Pivot can access localhost:{self.attacker_port} via localhost:{self.remote_port}")
            print(self.get_usage_info())
            return True

        return False

    def get_usage_info(self) -> str:
        """
        Get usage information

        Returns:
            Usage information string
        """
        info = f"\n[*] Use cases:"
        info += f"\n    - Pivot can download payloads from attacker"
        info += f"\n    - Pivot can connect to attacker C2"
        info += f"\n    - Pivot can upload exfiltrated data to attacker"
        info += f"\n    - Pivot can access attacker-hosted services"

        return info