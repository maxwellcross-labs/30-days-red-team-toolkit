"""
Dynamic Port Forward Tunnel
Create SOCKS proxy through pivot
"""

import subprocess
from pathlib import Path
from typing import List

from ..core.base_tunnel import BaseTunnel
from ..utils.config_generator import ProxychainsConfigGenerator


class DynamicForwardTunnel(BaseTunnel):
    """Dynamic port forwarding - SOCKS proxy (SSH -D)"""

    def __init__(
            self,
            pivot_host: str,
            pivot_user: str,
            pivot_key: str,
            socks_port: int = 1080,
            output_dir: Path = None
    ):
        """
        Initialize dynamic port forward tunnel

        Args:
            pivot_host: Pivot host IP/hostname
            pivot_user: SSH username for pivot
            pivot_key: Path to SSH private key
            socks_port: SOCKS proxy port (default: 1080)
            output_dir: Output directory for config files
        """
        super().__init__(pivot_host, pivot_user, pivot_key)

        self.socks_port = socks_port
        self.output_dir = output_dir or Path("ssh_tunnels")

        self.tunnel_info = {
            'type': 'socks_proxy',
            'pivot': f'{pivot_user}@{pivot_host}',
            'socks_port': socks_port
        }

    def establish(self) -> bool:
        """
        Establish SOCKS proxy

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Setting up DYNAMIC port forward (SOCKS proxy)...")
        print(f"[*] Pivot: {self.pivot_user}@{self.pivot_host}")
        print(f"[*] SOCKS port: {self.socks_port}")

        # SSH command: -D socks_port
        cmd = [
            'ssh',
            '-i', self.pivot_key,
            '-D', str(self.socks_port),
            '-N',  # Don't execute remote command
            '-f',  # Background
            f'{self.pivot_user}@{self.pivot_host}'
        ]

        if self._execute_ssh_command(cmd):
            self.is_active = True
            print(f"\n[+] SOCKS proxy established!")
            print(f"[+] Proxy: localhost:{self.socks_port}")
            print(self.get_usage_info())

            # Create proxychains config
            self._create_proxychains_config()

            return True

        return False

    def _create_proxychains_config(self):
        """Create proxychains configuration file"""
        config_gen = ProxychainsConfigGenerator(self.output_dir)
        config_file = config_gen.generate(self.socks_port)

        print(f"\n[+] Proxychains config created: {config_file}")
        print(f"[*] Use: proxychains4 -f {config_file} <command>")

    def test_connectivity(self, test_target: str) -> bool:
        """
        Test SOCKS proxy connectivity

        Args:
            test_target: Target URL to test

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[*] Testing SOCKS proxy...")
        print(f"[*] Proxy: localhost:{self.socks_port}")
        print(f"[*] Test target: {test_target}")

        cmd = f"curl --socks5 127.0.0.1:{self.socks_port} -m 5 {test_target}"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"\n[+] SOCKS proxy working!")
                print(f"[*] Response preview:")
                print(result.stdout[:200])
                return True
            else:
                print(f"\n[-] SOCKS proxy test failed")
                print(f"[*] Error: {result.stderr}")
                return False

        except Exception as e:
            print(f"\n[-] Test error: {e}")
            return False

    def get_usage_info(self) -> str:
        """
        Get usage information

        Returns:
            Usage information string
        """
        info = f"\n[*] Usage examples:"
        info += f"\n    proxychains: Edit /etc/proxychains.conf, add 'socks5 127.0.0.1 {self.socks_port}'"
        info += f"\n    nmap: nmap --proxy socks5://127.0.0.1:{self.socks_port} <target>"
        info += f"\n    curl: curl --socks5 127.0.0.1:{self.socks_port} http://<target>"
        info += f"\n    firefox: Set SOCKS proxy to localhost:{self.socks_port}"
        info += f"\n    metasploit: setg Proxies socks5:127.0.0.1:{self.socks_port}"

        return info