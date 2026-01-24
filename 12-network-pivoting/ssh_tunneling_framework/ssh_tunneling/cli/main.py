"""
SSH Tunneling Framework CLI
Command-line interface for SSH tunnel management
"""

import sys
import argparse
import time
from pathlib import Path

from ..core.tunnel_manager import TunnelManager
from ..tunnels.local_forward import LocalForwardTunnel
from ..tunnels.remote_forward import RemoteForwardTunnel
from ..tunnels.dynamic_forward import DynamicForwardTunnel
from ..tunnels.jump_host import JumpHostTunnel
from ..utils.process_manager import ProcessManager
from ..utils.validators import InputValidator


def print_banner():
    """Print framework banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          SSH TUNNELING FRAMEWORK v2.0                        ║
║          Professional Port Forwarding & SOCKS Proxy          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def setup_local_forward(args, manager: TunnelManager) -> bool:
    """Setup local port forward"""
    # Validate inputs
    is_valid, errors = InputValidator.validate_tunnel_params(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key
    )

    if not is_valid:
        print(f"\n[-] Validation errors:")
        for error in errors:
            print(f"    {error}")
        return False

    # Validate ports
    for port, name in [(args.target_port, "target"), (args.local_port, "local")]:
        is_valid, msg = InputValidator.validate_port(port)
        if not is_valid:
            print(f"\n[-] {msg}")
            return False
        elif msg:
            print(f"[!] {msg}")

    # Validate target host
    is_valid, msg = InputValidator.validate_hostname(args.target_host)
    if not is_valid:
        print(f"\n[-] {msg}")
        return False

    # Create tunnel
    tunnel = LocalForwardTunnel(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key,
        args.target_host,
        args.target_port,
        args.local_port
    )

    return manager.add_tunnel(tunnel)


def setup_remote_forward(args, manager: TunnelManager) -> bool:
    """Setup remote port forward"""
    # Validate inputs
    is_valid, errors = InputValidator.validate_tunnel_params(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key
    )

    if not is_valid:
        print(f"\n[-] Validation errors:")
        for error in errors:
            print(f"    {error}")
        return False

    # Validate ports
    for port, name in [(args.target_port, "attacker"), (args.remote_port, "remote")]:
        is_valid, msg = InputValidator.validate_port(port)
        if not is_valid:
            print(f"\n[-] {msg}")
            return False
        elif msg:
            print(f"[!] {msg}")

    # Create tunnel
    tunnel = RemoteForwardTunnel(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key,
        args.target_port,
        args.remote_port
    )

    return manager.add_tunnel(tunnel)


def setup_dynamic_forward(args, manager: TunnelManager) -> bool:
    """Setup SOCKS proxy"""
    # Validate inputs
    is_valid, errors = InputValidator.validate_tunnel_params(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key
    )

    if not is_valid:
        print(f"\n[-] Validation errors:")
        for error in errors:
            print(f"    {error}")
        return False

    # Validate SOCKS port
    is_valid, msg = InputValidator.validate_port(args.socks_port)
    if not is_valid:
        print(f"\n[-] {msg}")
        return False
    elif msg:
        print(f"[!] {msg}")

    # Create tunnel
    tunnel = DynamicForwardTunnel(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key,
        args.socks_port,
        manager.get_output_dir()
    )

    success = manager.add_tunnel(tunnel)

    # Test if requested
    if success and args.test:
        print(f"\n[*] Waiting 2 seconds for tunnel to establish...")
        time.sleep(2)
        tunnel.test_connectivity(args.test)

    return success


def setup_jump_host(args, manager: TunnelManager) -> bool:
    """Setup jump host tunnel"""
    # Validate inputs
    is_valid, errors = InputValidator.validate_tunnel_params(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key
    )

    if not is_valid:
        print(f"\n[-] Validation errors:")
        for error in errors:
            print(f"    {error}")
        return False

    # Create tunnel
    tunnel = JumpHostTunnel(
        args.pivot_host,
        args.pivot_user,
        args.pivot_key,
        args.target_host,
        args.target_user,
        args.target_key,
        args.local_port,
        args.target_port or 22
    )

    return manager.add_tunnel(tunnel)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SSH Tunneling Framework - Professional port forwarding and SOCKS proxy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Local forward:
    %(prog)s --type local --pivot-host 10.0.0.1 --pivot-user root --pivot-key ~/.ssh/id_rsa \\
             --target-host 192.168.1.100 --target-port 3389 --local-port 3389

  Remote forward:
    %(prog)s --type remote --pivot-host 10.0.0.1 --pivot-user root --pivot-key ~/.ssh/id_rsa \\
             --target-port 8080 --remote-port 80

  SOCKS proxy:
    %(prog)s --type dynamic --pivot-host 10.0.0.1 --pivot-user root --pivot-key ~/.ssh/id_rsa \\
             --socks-port 1080 --test http://internal-server

  List active tunnels:
    %(prog)s --list

  Kill all tunnels:
    %(prog)s --kill-all
        """
    )

    # Common arguments
    parser.add_argument('--pivot-host', type=str,
                        help='Pivot host IP/hostname')
    parser.add_argument('--pivot-user', type=str,
                        help='Pivot SSH username')
    parser.add_argument('--pivot-key', type=str,
                        help='Path to SSH private key')

    # Tunnel type
    parser.add_argument('--type', type=str,
                        choices=['local', 'remote', 'dynamic', 'jump'],
                        help='Tunnel type')

    # Local forward arguments
    parser.add_argument('--target-host', type=str,
                        help='Target host (for local/jump forward)')
    parser.add_argument('--target-port', type=int,
                        help='Target port')
    parser.add_argument('--local-port', type=int,
                        help='Local port')

    # Remote forward arguments
    parser.add_argument('--remote-port', type=int,
                        help='Remote port (for remote forward)')

    # Dynamic forward arguments
    parser.add_argument('--socks-port', type=int, default=1080,
                        help='SOCKS port (default: 1080)')
    parser.add_argument('--test', type=str,
                        help='Test target for SOCKS proxy')

    # Jump host arguments
    parser.add_argument('--target-user', type=str,
                        help='Target SSH username (for jump host)')
    parser.add_argument('--target-key', type=str,
                        help='Path to target SSH key (for jump host)')

    # Management commands
    parser.add_argument('--list', action='store_true',
                        help='List active tunnels')
    parser.add_argument('--list-processes', action='store_true',
                        help='List all SSH tunnel processes')
    parser.add_argument('--kill-all', action='store_true',
                        help='Kill all SSH tunnels')

    # Output directory
    parser.add_argument('--output-dir', type=str, default='ssh_tunnels',
                        help='Output directory (default: ssh_tunnels)')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Handle management commands
    if args.kill_all:
        ProcessManager.kill_all_tunnels()
        return 0

    if args.list_processes:
        ProcessManager.list_processes()
        return 0

    # Initialize manager
    manager = TunnelManager(args.output_dir)

    if args.list:
        manager.list_active_tunnels()
        return 0

    # Validate required arguments for tunnel creation
    if not args.type:
        print("\n[-] Error: --type is required for tunnel creation")
        print("[*] Use --help for usage information")
        return 1

    if not all([args.pivot_host, args.pivot_user, args.pivot_key]):
        print("\n[-] Error: --pivot-host, --pivot-user, and --pivot-key are required")
        return 1

    # Setup tunnel based on type
    success = False

    if args.type == 'local':
        if not all([args.target_host, args.target_port, args.local_port]):
            print("\n[-] Error: Local forward requires --target-host, --target-port, --local-port")
            return 1
        success = setup_local_forward(args, manager)

    elif args.type == 'remote':
        if not all([args.target_port, args.remote_port]):
            print("\n[-] Error: Remote forward requires --target-port, --remote-port")
            return 1
        success = setup_remote_forward(args, manager)

    elif args.type == 'dynamic':
        success = setup_dynamic_forward(args, manager)

    elif args.type == 'jump':
        if not all([args.target_host, args.target_user, args.target_key, args.local_port]):
            print("\n[-] Error: Jump host requires --target-host, --target-user, --target-key, --local-port")
            return 1
        success = setup_jump_host(args, manager)

    # Show summary
    print(f"\n" + "=" * 60)
    manager.list_active_tunnels()
    print(f"=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())