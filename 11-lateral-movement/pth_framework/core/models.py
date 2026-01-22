"""
Data models for Pass-the-Hash Framework
Type-safe dataclasses for authentication results and credentials
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class AuthMethod(Enum):
    """Supported authentication methods"""
    SMB_CME = "SMB-CME"
    WMI_IMPACKET = "WMI-Impacket"
    PSEXEC_IMPACKET = "PSExec-Impacket"
    RDP_PTH = "RDP-PtH"


class AccessLevel(Enum):
    """Access level achieved on target"""
    NONE = "None"
    USER = "User"
    ADMIN = "Admin"


@dataclass
class Credential:
    """Credential data structure"""
    username: str
    ntlm_hash: str
    domain: str = "."

    def __str__(self) -> str:
        return f"{self.domain}\\{self.username}"

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'ntlm_hash': self.ntlm_hash,
            'domain': self.domain
        }


@dataclass
class AuthResult:
    """Authentication attempt result"""
    target: str
    username: str
    domain: str
    method: AuthMethod
    success: bool
    access_level: AccessLevel = AccessLevel.NONE
    command: Optional[str] = None
    output: Optional[str] = None
    note: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'target': self.target,
            'username': self.username,
            'domain': self.domain,
            'method': self.method.value,
            'success': self.success,
            'access_level': self.access_level.value,
            'command': self.command,
            'output': self.output,
            'note': self.note,
            'timestamp': self.timestamp.isoformat(),
            'error_message': self.error_message
        }


@dataclass
class SprayResult:
    """Results from hash spraying operation"""
    successful: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    admin_access: List[str] = field(default_factory=list)
    total_targets: int = 0

    def to_dict(self) -> dict:
        return {
            'successful': self.successful,
            'failed': self.failed,
            'admin_access': self.admin_access,
            'total_targets': self.total_targets,
            'success_rate': f"{len(self.successful)}/{self.total_targets}"
        }


@dataclass
class FrameworkConfig:
    """Configuration for the PTH framework"""
    output_dir: str = "pth_results"
    timeout: int = 30
    verbose: bool = True