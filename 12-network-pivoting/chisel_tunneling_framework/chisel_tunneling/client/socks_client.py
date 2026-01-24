import subprocess
import time
from ..core.base_tunnel import BaseTunnel


class SocksClient(BaseTunnel):
    """SOCKS5 proxy client"""

    def __init__(self, server_ip: str, server_port: int, socks_port: int = 1080):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.socks_port = socks_port
        self.tunnel_info = {'type': 'socks', 'server': f'{server_ip}:{server_port}', 'socks_port': socks_port}

    def start(self) -> bool:
        print(f"\n[*] Connecting SOCKS client to {self.server_ip}:{self.server_port}...")
        cmd = ['chisel', 'client', f'{self.server_ip}:{self.server_port}', f'R:{self.socks_port}:socks']

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            if self.is_running():
                self.is_active = True
                print(f"[+] SOCKS proxy ready at localhost:{self.socks_port}")
                return True
        except Exception as e:
            print(f"[-] Error: {e}")
        return False

    def stop(self) -> bool:
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            return True
        return False

    def get_command_for_pivot(self) -> str:
        return f"chisel client {self.server_ip}:{self.server_port} R:{self.socks_port}:socks"