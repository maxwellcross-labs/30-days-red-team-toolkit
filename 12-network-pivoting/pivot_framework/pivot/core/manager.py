import json
from pathlib import Path
from ..pivots.host import PivotHost
from ..forwards.ssh import SSHForwarder
from ..chains.builder import ChainBuilder
from ..utils.visualizer import print_topology


class PivotManager:
    def __init__(self, output_dir="port_forwards"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.pivots = []  # List[PivotHost]
        self.active_forwards = []
        self.chain_builder = ChainBuilder(self.output_dir)

        print(f"[+] Framework initialized at: {self.output_dir}")

    def add_pivot(self, name, ip, user, key, networks):
        pivot = PivotHost(name, ip, user, key, networks)
        self.pivots.append(pivot)
        print(f"[+] Added pivot: {name} ({ip})")
        self._save_state()

    def get_pivot(self, name):
        return next((p for p in self.pivots if p.name == name), None)

    def forward_port(self, pivot_name, target_host, target_port, local_port):
        pivot = self.get_pivot(pivot_name)
        if not pivot:
            print(f"[-] Pivot not found: {pivot_name}")
            return

        print(f"[*] Setting up forward via {pivot.name}...")
        if SSHForwarder.start_local_forward(pivot, local_port, target_host, target_port):
            print(f"[+] Forward established: localhost:{local_port} -> {target_host}:{target_port}")
            self.active_forwards.append({
                'pivot': pivot_name,
                'target': f'{target_host}:{target_port}',
                'local_port': local_port
            })
            self._save_state()

    def setup_socks(self, pivot_name, socks_port=1080):
        pivot = self.get_pivot(pivot_name)
        if not pivot:
            print(f"[-] Pivot not found")
            return

        print(f"[*] Setting up SOCKS via {pivot.name}...")
        if SSHForwarder.start_dynamic_forward(pivot, socks_port):
            conf = self.chain_builder.create_config(socks_port, pivot.name)
            print(f"[+] SOCKS Ready. Config: {conf}")

    def visualize(self):
        print_topology(self.pivots, self.active_forwards)

    def _save_state(self):
        config_file = self.output_dir / "pivot_state.json"
        data = {
            'pivots': [p.to_dict() for p in self.pivots],
            'forwards': self.active_forwards
        }
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)