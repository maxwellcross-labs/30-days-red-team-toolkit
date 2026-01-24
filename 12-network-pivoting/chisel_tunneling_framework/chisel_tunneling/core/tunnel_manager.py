from pathlib import Path
from typing import List


class TunnelManager:
    """Manage Chisel tunnels"""

    def __init__(self, output_dir: str = "chisel_tunnels"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.server = None
        self.clients: List = []
        print(f"[+] Chisel Framework initialized: {self.output_dir}")

    def set_server(self, server) -> bool:
        if server.start():
            self.server = server
            return True
        return False

    def add_client(self, client) -> bool:
        if client.start():
            self.clients.append(client)
            return True
        return False

    def list_active_tunnels(self):
        print("\n" + "=" * 60)
        print("ACTIVE CHISEL TUNNELS")
        print("=" * 60)
        if self.server:
            print(f"\n[SERVER] {self.server.get_info()}")
        for i, client in enumerate(self.clients, 1):
            print(f"\n[CLIENT {i}] {client.get_info()}")
        if not self.server and not self.clients:
            print("\n[*] No active tunnels")

    def stop_all(self):
        if self.server:
            self.server.stop()
        for client in self.clients:
            client.stop()

    def get_output_dir(self) -> Path:
        return self.output_dir