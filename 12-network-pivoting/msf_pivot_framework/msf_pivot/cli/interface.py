import argparse
import sys
from ..core.manager import PivotManager


def main():
    parser = argparse.ArgumentParser(description="Metasploit Pivoting Automation")
    parser.add_argument('--session', type=int, required=True, help='Meterpreter session ID')
    parser.add_argument('--type', type=str, required=True,
                        choices=['route', 'socks', 'portfwd', 'complete'],
                        help='Script type')

    # Network args
    parser.add_argument('--network', type=str, help='Target network')
    parser.add_argument('--netmask', type=str, default='255.255.255.0', help='Network mask')

    # Port args
    parser.add_argument('--socks-port', type=int, default=1080, help='SOCKS port')
    parser.add_argument('--local-port', type=int, help='Local port (for portfwd)')
    parser.add_argument('--remote-host', type=str, help='Remote host (for portfwd)')
    parser.add_argument('--remote-port', type=int, help='Remote port (for portfwd)')

    args = parser.parse_args()
    manager = PivotManager()

    if args.type == 'route':
        if not args.network:
            print("[-] Error: --network required for route")
            sys.exit(1)
        manager.create_route(args.session, args.network, args.netmask)

    elif args.type == 'socks':
        manager.create_socks(args.session, args.socks_port)

    elif args.type == 'portfwd':
        if not all([args.local_port, args.remote_host, args.remote_port]):
            print("[-] Error: Portfwd requires --local-port, --remote-host, --remote-port")
            sys.exit(1)
        manager.create_portfwd(args.session, args.local_port, args.remote_host, args.remote_port)

    elif args.type == 'complete':
        if not args.network:
            print("[-] Error: --network required for complete setup")
            sys.exit(1)
        manager.create_complete_setup(args.session, args.network, args.netmask, args.socks_port)


if __name__ == "__main__":
    main()