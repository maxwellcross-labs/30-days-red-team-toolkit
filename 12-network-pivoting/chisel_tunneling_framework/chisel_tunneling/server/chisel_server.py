import subprocess
import time
from pathlib import Path
from ..core.base_tunnel import BaseTunnel


class ChiselServer(BaseTunnel):
    """Chisel server"""

    def __init__(self, port: int = 8080, reverse: bool = True, socks5: bool = True, output_dir: Path = None):
        super().__init__()
        self.port = port
        self.reverse = reverse
        self.socks5 = socks5
        self.output_dir = output_dir or Path("chisel_tunnels")
        self.tunnel_info = {'type': 'server', 'port': port, 'reverse': reverse, 'socks5': socks5}

    def start(self) -> bool:
        print(f"\n[*] Starting Chisel server on port {self.port}...")
        cmd = ['chisel', 'server', '-p', str(self.port)]
        if self.reverse:
            cmd.append('--reverse')
        if self.socks5:
            cmd.append('--socks5')

        log_file = self.output_dir / "chisel_server.log"
        self.output_dir.mkdir(exist_ok=True)
        cmd.extend(['--log', str(log_file)])

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            if self.is_running():
                self.is_active = True
                print(f"[+] Server started! PID: {self.process.pid}")
                print(f"[+] Listening on 0.0.0.0:{self.port}")
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