"""
Data models for Remote Execution Framework
Type-safe dataclasses for execution results and credentials
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class ExecutionMethod(Enum):
    """Supported remote execution methods"""
    WMI = "WMI"
    PSREMOTING = "PSRemoting"
    DCOM = "DCOM"


class AuthType(Enum):
    """Authentication type used"""
    PASSWORD = "password"
    HASH = "hash"


@dataclass
class Credential:
    """Credential data structure supporting both password and hash auth"""
    username: str
    domain: str = "."
    password: Optional[str] = None
    ntlm_hash: Optional[str] = None

    def __post_init__(self):
        """Validate that at least one auth method is provided"""
        if not self.password and not self.ntlm_hash:
            raise ValueError("Must provide either password or ntlm_hash")

    @property
    def auth_type(self) -> AuthType:
        """Determine which auth type to use (prefer password)"""
        return AuthType.PASSWORD if self.password else AuthType.HASH

    def __str__(self) -> str:
        return f"{self.domain}\\{self.username}"

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'domain': self.domain,
            'auth_type': self.auth_type.value
        }


@dataclass
class ExecutionResult:
    """Result from a remote execution attempt"""
    target: str
    method: ExecutionMethod
    command: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'target': self.target,
            'method': self.method.value,
            'command': self.command,
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MultiTargetResult:
    """Results from multi-target execution"""
    successful: List[dict] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    total_targets: int = 0

    def to_dict(self) -> dict:
        return {
            'successful': self.successful,
            'failed': self.failed,
            'total_targets': self.total_targets,
            'success_rate': f"{len(self.successful)}/{self.total_targets}"
        }


@dataclass
class BeaconDeployResult:
    """Result from beacon deployment"""
    target: str
    beacon_path: str
    copy_success: bool
    exec_success: bool
    method: ExecutionMethod
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.copy_success and self.exec_success

    def to_dict(self) -> dict:
        return {
            'target': self.target,
            'beacon_path': self.beacon_path,
            'copy_success': self.copy_success,
            'exec_success': self.exec_success,
            'method': self.method.value,
            'overall_success': self.success,
            'error': self.error
        }


@dataclass
class FrameworkConfig:
    """Configuration for the Remote Execution framework"""
    output_dir: str = "remote_exec"
    timeout: int = 30
    verbose: bool = True