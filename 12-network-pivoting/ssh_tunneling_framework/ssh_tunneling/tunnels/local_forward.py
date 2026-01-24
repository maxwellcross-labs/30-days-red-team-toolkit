"""
Local Port Forward Tunnel
Forward local port to remote target through pivot
"""

from typing import List

from ..core.base_tunnel import BaseTunnel


class LocalForwardTunnel(BaseTunnel):
    """Local port forwarding (SSH -L)"""

    def __init__(
            self,
            pivot_host: str,
            pivot_user: str,
            pivot_key: str,
            target_host: str,
            target_port: int,
            local_port: int
    ):
        """
        Initialize local port forward tunnel

        Args:
            pivot_host: Pivot host IP/hostname
            pivot_user: SSH username for pivot
            pivot_key: Path to SSH private key
            target_host: Target host to forward to
            target_port: Target port to forward to
            local_port: Local port to bind
        """
        super().__init__(pivot_host, pivot_user, pivot_key)

        self.target_host = target_host
        self.target_port = target_port
        self.local_port = local_port

        self.tunnel_info = {
            'type': 'local_forward',
            'pivot': f'{pivot_user}@{pivot_host}',
            'target': f'{target_host}:{target_port}',
            'local_port': local_port
        }

    def establish(self) -> bool:
        """
        Establish local port forward

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Setting up LOCAL port forward...")
        print(f"[*] Pivot: {self.pivot_user}@{self.pivot_host}")
        print(f"[*] Target: {self.target_host}:{self.target_port}")
        print(f"[*] Local port: {self.local_port}")

        # SSH command: -L local_port:target_host:target_port
        cmd = [
            'ssh',
            '-i', self.pivot_key,
            '-L', f'{self.local_port}:{self.target_host}:{self.target_port}',
            '-N',  # Don't execute remote command
            '-f',  # Background
            f'{self.pivot_user}@{self.pivot_host}'
        ]

        if self._execute_ssh_command(cmd):
            self.is_active = True
            print(f"\n[+] Local port forward established!")
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
        info = f"\n[*] Example usage:"
        info += f"\n    rdp: xfreerdp /v:localhost:{self.local_port}"
        info += f"\n    ssh: ssh user@localhost -p {self.local_port}"
        info += f"\n    smb: smbclient -L localhost -p {self.local_port}"
        info += f"\n    http: curl http://localhost:{self.local_port}"

        return info