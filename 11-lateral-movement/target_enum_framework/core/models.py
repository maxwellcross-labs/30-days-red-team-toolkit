"""
Data models for Target Enumeration Framework
Type-safe dataclasses for hosts, targets, and scan results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Set


class Protocol(Enum):
    """Supported network protocols"""
    SMB = "SMB"
    WINRM = "WinRM"
    RDP = "RDP"
    SSH = "SSH"
    WMI = "WMI"


class OperatingSystem(Enum):
    """Target operating system"""
    WINDOWS = "Windows"
    LINUX = "Linux"
    UNKNOWN = "Unknown"


class TargetCategory(Enum):
    """Target classification categories"""
    DOMAIN_CONTROLLER = "Domain Controller"
    FILE_SERVER = "File Server"
    DATABASE = "Database Server"
    MAIL_SERVER = "Mail Server"
    BACKUP_SERVER = "Backup Server"
    WEB_SERVER = "Web Server"
    WORKSTATION = "Workstation"
    HIGH_VALUE = "High Value"
    STANDARD = "Standard"


@dataclass
class HostInfo:
    """Information about a discovered host"""
    ip: str
    hostname: Optional[str] = None
    os: OperatingSystem = OperatingSystem.UNKNOWN
    protocols: List[Protocol] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    categories: List[TargetCategory] = field(default_factory=list)
    raw_output: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)

    def add_protocol(self, protocol: Protocol, port: int = None):
        """Add discovered protocol"""
        if protocol not in self.protocols:
            self.protocols.append(protocol)
        if port and port not in self.ports:
            self.ports.append(port)

    def add_category(self, category: TargetCategory):
        """Add target category"""
        if category not in self.categories:
            self.categories.append(category)

    @property
    def is_windows(self) -> bool:
        return self.os == OperatingSystem.WINDOWS

    @property
    def is_linux(self) -> bool:
        return self.os == OperatingSystem.LINUX

    @property
    def is_high_value(self) -> bool:
        return TargetCategory.HIGH_VALUE in self.categories

    @property
    def is_domain_controller(self) -> bool:
        return TargetCategory.DOMAIN_CONTROLLER in self.categories

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ip': self.ip,
            'hostname': self.hostname,
            'os': self.os.value,
            'protocols': [p.value for p in self.protocols],
            'ports': self.ports,
            'categories': [c.value for c in self.categories],
            'raw_output': self.raw_output,
            'discovered_at': self.discovered_at.isoformat()
        }


@dataclass
class ScanResult:
    """Result from a protocol scan"""
    protocol: Protocol
    network: str
    hosts_found: List[HostInfo] = field(default_factory=list)
    scan_duration: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    @property
    def count(self) -> int:
        return len(self.hosts_found)

    def to_dict(self) -> dict:
        return {
            'protocol': self.protocol.value,
            'network': self.network,
            'hosts_found': len(self.hosts_found),
            'scan_duration': self.scan_duration,
            'error': self.error
        }


@dataclass
class TargetCollection:
    """Collection of enumerated targets organized by type"""
    windows_hosts: Dict[str, HostInfo] = field(default_factory=dict)
    linux_hosts: Dict[str, HostInfo] = field(default_factory=dict)
    domain_controllers: Dict[str, HostInfo] = field(default_factory=dict)
    high_value: Dict[str, HostInfo] = field(default_factory=dict)
    all_hosts: Dict[str, HostInfo] = field(default_factory=dict)

    def add_host(self, host: HostInfo):
        """Add or update host in collection"""
        ip = host.ip

        # Update or add to all_hosts
        if ip in self.all_hosts:
            existing = self.all_hosts[ip]
            # Merge protocols
            for proto in host.protocols:
                existing.add_protocol(proto)
            # Merge ports
            for port in host.ports:
                if port not in existing.ports:
                    existing.ports.append(port)
            # Merge categories
            for cat in host.categories:
                existing.add_category(cat)
            # Update OS if we learned it
            if host.os != OperatingSystem.UNKNOWN:
                existing.os = host.os
            host = existing
        else:
            self.all_hosts[ip] = host

        # Categorize by OS
        if host.is_windows:
            self.windows_hosts[ip] = host
        elif host.is_linux:
            self.linux_hosts[ip] = host

        # Categorize special types
        if host.is_domain_controller:
            self.domain_controllers[ip] = host
            self.high_value[ip] = host

        if host.is_high_value:
            self.high_value[ip] = host

    def get_ips_by_category(self, category: str) -> List[str]:
        """Get list of IPs for a category"""
        category_map = {
            'windows': self.windows_hosts,
            'linux': self.linux_hosts,
            'domain_controllers': self.domain_controllers,
            'high_value': self.high_value,
            'all': self.all_hosts
        }
        return list(category_map.get(category, {}).keys())

    def to_dict(self) -> dict:
        return {
            'windows_hosts': [h.to_dict() for h in self.windows_hosts.values()],
            'linux_hosts': [h.to_dict() for h in self.linux_hosts.values()],
            'domain_controllers': [h.to_dict() for h in self.domain_controllers.values()],
            'high_value': [h.to_dict() for h in self.high_value.values()],
            'all_hosts': [h.to_dict() for h in self.all_hosts.values()]
        }


@dataclass
class FrameworkConfig:
    """Configuration for the Target Enumeration framework"""
    output_dir: str = "lm_targets"
    timeout: int = 300
    verbose: bool = True


# High-value target keywords for identification
HIGH_VALUE_KEYWORDS = [
    # Domain Controllers
    ('DC', TargetCategory.DOMAIN_CONTROLLER),
    ('DOMAIN', TargetCategory.DOMAIN_CONTROLLER),
    ('CONTROLLER', TargetCategory.DOMAIN_CONTROLLER),
    ('AD', TargetCategory.DOMAIN_CONTROLLER),

    # File Servers
    ('FILE', TargetCategory.FILE_SERVER),
    ('FS', TargetCategory.FILE_SERVER),
    ('SHARE', TargetCategory.FILE_SERVER),
    ('NAS', TargetCategory.FILE_SERVER),

    # Databases
    ('SQL', TargetCategory.DATABASE),
    ('DATABASE', TargetCategory.DATABASE),
    ('DB', TargetCategory.DATABASE),
    ('ORACLE', TargetCategory.DATABASE),
    ('MYSQL', TargetCategory.DATABASE),

    # Mail Servers
    ('EXCHANGE', TargetCategory.MAIL_SERVER),
    ('MAIL', TargetCategory.MAIL_SERVER),
    ('SMTP', TargetCategory.MAIL_SERVER),

    # Backup
    ('BACKUP', TargetCategory.BACKUP_SERVER),
    ('BKP', TargetCategory.BACKUP_SERVER),

    # Sensitive
    ('VAULT', TargetCategory.HIGH_VALUE),
    ('SECRET', TargetCategory.HIGH_VALUE),
    ('ADMIN', TargetCategory.HIGH_VALUE),
    ('MGMT', TargetCategory.HIGH_VALUE),
]