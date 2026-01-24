"""
Jump Host Tunnel
Connect to target through jump host
"""

from typing import List

from ..core.base_tunnel import BaseTunnel


class JumpHostTunnel(BaseTunnel):
    """Jump host tunneling (SSH -J)"""

    def __init__(
            self,
            jump_host: str,
            jump_user: str,
            jump_key: str,
            target_host: str,
            target_user: str,
            target_key: str,
            local_port: int,
            target_port: int = 22
    ):
        """
        Initialize jump host tunnel

        Args:
            jump_host: Jump host IP/hostname
            jump_user: SSH username for jump host
            jump_key: Path to SSH private key for jump host
            target_host: Target host IP/hostname
            target_user: SSH username for target
            target_key: Path to SSH private key for target
            local_port: Local port to bind
            target_port: Target port (default: 22)
        """
        super().__init__(jump_host, jump_user, jump_key)

        self.target_host = target_host
        self.target_user = target_user
        self.target_key = target_key
        self.local_port = local_port
        self.target_port = target_port

        self.tunnel_info = {
            'type': 'jump_host',
            'jump_host': f'{jump_user}@{jump_host}',
            'target': f'{target_user}@{target_host}',
            'local_port': local_port,
            'target_port': target_port
        }

    def establish(self) -> bool:
        """
        Establish jump host tunnel

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Setting up jump host tunnel...")
        print(f"[*] Jump host: {self.pivot_user}@{self.pivot_host}")
        print(f"[*] Target: {self.target_user}@{self.target_host}")
        print(f"[*] Local port: {self.local_port}")

        # SSH command with ProxyJump
        cmd = [
            'ssh',
            '-i', self.target_key,
            '-J', f'{self.pivot_user}@{self.pivot_host}',
            '-L', f'{self.local_port}:{self.target_host}:{self.target_port}',
            '-N',  # Don't execute remote command
            '-f',  # Background
            f'{self.target_user}@{self.target_host}'
        ]

        if self._execute_ssh_command(cmd):
            self.is_active = True
            print(f"\n[+] Jump host tunnel established!")
            print(f"[+] Access {self.target_host}:{self.target_port} via localhost:{self.local_port}")
            print(self.get_usage_info())
            return True

        return False

    def get_usage_info(self) -> str:
        """
        Get usage information

        Returns:
            Usage information string
        """
        info = f"\n[*] Usage:"
        info += f"\n    ssh: ssh -p {self.local_port} {self.target_user}@localhost"
        info += f"\n    Direct access to {self.target_host} through {self.pivot_host}"

        return info