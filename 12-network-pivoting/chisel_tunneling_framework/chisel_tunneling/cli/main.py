import sys
import argparse
import time
from ..core.tunnel_manager import TunnelManager
from ..server.chisel_server import ChiselServer
from ..client.socks_client import SocksClient
from ..utils.binary_manager import BinaryManager
from ..utils.deployment import DeploymentManager
from ..utils.process_manager import ProcessManager


def main():
    parser = argparse.ArgumentParser(description="Chisel Tunneling Framework")
    parser.add_argument('--mode', choices=['server', 'client', 'deploy'], help='Operation mode')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--server-ip', type=str, help='Server IP')
    parser.add_argument('--server-port', type=int, help='Server port')
    parser.add_argument('--socks-port', type=int, default=1080, help='SOCKS port')
    parser.add_argument('--pivot-ip', type=str, help='Pivot IP')
    parser.add_argument('--pivot-user', type=str, help='Pivot user')
    parser.add_argument('--pivot-key', type=str, help='SSH key')
    parser.add_argument('--chisel-binary', type=str, help='Chisel binary')
    parser.add_argument('--check', action='store_true', help='Check Chisel')
    parser.add_argument('--kill-all', action='store_true', help='Kill all')
    parser.add_argument('--list', action='store_true', help='List tunnels')

    args = parser.parse_args()

    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║         CHISEL TUNNELING FRAMEWORK v2.0                 ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    if args.check:
        is_installed, msg = BinaryManager.check_chisel()
        if not is_installed:
            print(BinaryManager.get_installation_instructions())
        return 0

    if args.kill_all:
        ProcessManager.kill_all_chisel()
        return 0

    manager = TunnelManager()

    if args.list:
        manager.list_active_tunnels()
        return 0

    if args.mode == 'server':
        server = ChiselServer(port=args.port)
        if manager.set_server(server):
            print("\n[*] Server running. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_all()

    elif args.mode == 'client':
        client = SocksClient(args.server_ip, args.server_port, args.socks_port)
        manager.add_client(client)

    elif args.mode == 'deploy':
        server = ChiselServer(port=args.port)
        manager.set_server(server)
        time.sleep(2)

        client = SocksClient(args.server_ip, args.server_port, args.socks_port)
        client_cmd = client.get_command_for_pivot()

        DeploymentManager.deploy_and_start(
            args.pivot_ip,
            args.pivot_user,
            args.pivot_key,
            args.chisel_binary,
            client_cmd
        )

    manager.list_active_tunnels()
    return 0


if __name__ == "__main__":
    sys.exit(main())