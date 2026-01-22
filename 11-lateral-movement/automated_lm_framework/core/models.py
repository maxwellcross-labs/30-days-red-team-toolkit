"""
Data models for Automated Lateral Movement Framework
Type-safe dataclasses for credentials, access entries, and movement chains
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class CredentialType(Enum):
    """Type of credential"""
    PASSWORD = "password"
    HASH = "hash"


class AccessLevel(Enum):
    """Access level achieved on target"""
    NONE = "none"
    USER = "user"
    ADMIN = "admin"


class ExecutionMethod(Enum):
    """Execution method for lateral movement"""
    SMB = "smb"
    WMI = "wmi"
    PSEXEC = "psexec"


@dataclass
class Credential:
    """
    Credential data structure
    Supports both password and hash authentication
    """
    username: str
    domain: str = "."
    password: Optional[str] = None
    ntlm_hash: Optional[str] = None

    def __post_init__(self):
        """Validate and determine credential type"""
        if not self.password and not self.ntlm_hash:
            raise ValueError("Must provide either password or ntlm_hash")

    @property
    def cred_type(self) -> CredentialType:
        """Determine credential type based on what's provided"""
        # Hash takes precedence if both provided
        if self.ntlm_hash:
            return CredentialType.HASH
        return CredentialType.PASSWORD

    @property
    def secret(self) -> str:
        """Get the authentication secret (hash or password)"""
        return self.ntlm_hash if self.ntlm_hash else self.password

    def __str__(self) -> str:
        return f"{self.domain}\\{self.username}"

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'domain': self.domain,
            'type': self.cred_type.value
        }


@dataclass
class AccessEntry:
    """
    Represents successful access to a target
    Used in the access matrix
    """
    target: str
    credential: Credential
    access_level: AccessLevel
    method: ExecutionMethod = ExecutionMethod.SMB
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_admin(self) -> bool:
        return self.access_level == AccessLevel.ADMIN

    def to_dict(self) -> dict:
        return {
            'target': self.target,
            'username': self.credential.username,
            'domain': self.credential.domain,
            'access_level': self.access_level.value,
            'method': self.method.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MovementStep:
    """
    Single step in the lateral movement chain
    Records execution details and output
    """
    target: str
    credential: Credential
    command: str
    output: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            'target': self.target,
            'username': self.credential.username,
            'domain': self.credential.domain,
            'command': self.command,
            'output': self.output,
            'success': self.success,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class BeaconDeployment:
    """Result of beacon deployment to a target"""
    target: str
    credential: Credential
    beacon_name: str
    copy_success: bool = False
    exec_success: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        return self.copy_success and self.exec_success

    def to_dict(self) -> dict:
        return {
            'target': self.target,
            'username': self.credential.username,
            'domain': self.credential.domain,
            'beacon_name': self.beacon_name,
            'copy_success': self.copy_success,
            'exec_success': self.exec_success,
            'overall_success': self.success,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AccessMatrix:
    """
    Complete access matrix showing all valid credential/target pairs
    """
    entries: List[AccessEntry] = field(default_factory=list)

    def add_entry(self, entry: AccessEntry):
        """Add access entry to matrix"""
        self.entries.append(entry)

    def get_admin_access(self) -> List[AccessEntry]:
        """Get all entries with admin access"""
        return [e for e in self.entries if e.is_admin]

    def get_user_access(self) -> List[AccessEntry]:
        """Get all entries with user-level access"""
        return [e for e in self.entries if e.access_level == AccessLevel.USER]

    def get_targets_with_admin(self) -> List[str]:
        """Get unique targets where we have admin"""
        return list(set(e.target for e in self.get_admin_access()))

    def to_dict(self) -> dict:
        return {
            'total_entries': len(self.entries),
            'admin_access': len(self.get_admin_access()),
            'user_access': len(self.get_user_access()),
            'entries': [e.to_dict() for e in self.entries]
        }


@dataclass
class MovementChain:
    """
    Complete lateral movement chain
    Tracks all movement steps and compromised hosts
    """
    steps: List[MovementStep] = field(default_factory=list)
    compromised_hosts: List[str] = field(default_factory=list)

    def add_step(self, step: MovementStep):
        """Add step to movement chain"""
        self.steps.append(step)
        if step.success and step.target not in self.compromised_hosts:
            self.compromised_hosts.append(step.target)

    def get_successful_steps(self) -> List[MovementStep]:
        """Get all successful movement steps"""
        return [s for s in self.steps if s.success]

    def to_dict(self) -> dict:
        return {
            'total_steps': len(self.steps),
            'successful_steps': len(self.get_successful_steps()),
            'compromised_hosts': self.compromised_hosts,
            'steps': [s.to_dict() for s in self.steps]
        }


@dataclass
class FrameworkConfig:
    """Configuration for the Automated LM framework"""
    output_dir: str = "automated_lm"
    timeout: int = 30
    test_timeout: int = 10
    verbose: bool = True