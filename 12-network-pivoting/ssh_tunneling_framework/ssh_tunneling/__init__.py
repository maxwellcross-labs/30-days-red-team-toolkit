"""
SSH Tunneling Framework
Professional SSH port forwarding and SOCKS proxy management
"""

__version__ = "2.0.0"
__author__ = "Maxwell Cross"

from .core.tunnel_manager import TunnelManager
from .tunnels.local_forward import LocalForwardTunnel
from .tunnels.remote_forward import RemoteForwardTunnel
from .tunnels.dynamic_forward import DynamicForwardTunnel
from .tunnels.jump_host import JumpHostTunnel

__all__ = [
    'TunnelManager',
    'LocalForwardTunnel',
    'RemoteForwardTunnel',
    'DynamicForwardTunnel',
    'JumpHostTunnel',
]