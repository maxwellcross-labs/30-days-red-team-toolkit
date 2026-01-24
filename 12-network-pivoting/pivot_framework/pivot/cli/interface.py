import argparse
import sys
from ..core.manager import PivotManager


def main():
    parser = argparse.ArgumentParser(description="Professional Pivot Framework")

    # Commands
    parser.add_argument('--add-pivot', action='store_true', help='Register a new pivot')
    parser.add_argument('--forward', action='store_true', help='Create port forward')
    parser.add_argument('--socks', action='store_true', help='Create SOCKS proxy')
    parser.add_argument('--visualize', action='store_true', help='Show topology')

    # Pivot Details
    parser.add_argument('--name', type=str)
    parser.add_argument('--ip', type=str)
    parser.add_argument('--user', type=str)
    parser.add_argument('--key', type=str)
    parser.add_argument('--networks', type=str)

    # Forwarding Details
    parser.add_argument('--pivot-name', type=str)
    parser.add_argument('--target-host', type=str)
    parser.add_argument('--target-port', type=int)
    parser.add_argument('--local-port', type=int)
    parser.add_argument('--socks-port', type=int, default=1080)

    args = parser.parse_args()
    manager = PivotManager()

    if args.add_pivot:
        if not all([args.name, args.ip, args.user, args.key, args.networks]):
            print("[-] Missing args for add-pivot")
            sys.exit(1)
        manager.add_pivot(args.name, args.ip, args.user, args.key, args.networks.split(','))

    elif args.forward:
        manager.forward_port(args.pivot_name, args.target_host, args.target_port, args.local_port)

    elif args.socks:
        manager.setup_socks(args.pivot_name, args.socks_port)

    # Always show status at end
    manager.visualize()


if __name__ == "__main__":
    main()