"""
Compromised System Model
========================

Represents a system that has been compromised during the operation.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .enums import Platform, PrivilegeLevel
from .credential import Credential


@dataclass
class CompromisedSystem:
    """
    Represents a compromised system in the operation.

    Attributes:
        hostname: System hostname
        ip_address: IP address of the system
        platform: Operating system (Windows/Linux)
        privilege_level: Current access level on the system
        credentials_harvested: Credentials found on this system
        pivot_capable: Whether system can be used as a pivot point
        reachable_networks: Networks this system can access
        compromised_at: When access was gained
        access_method: How the system was compromised
        notes: Additional notes about the system
    """
    hostname: str
    ip_address: str
    platform: Platform
    privilege_level: PrivilegeLevel
    credentials_harvested: List[Credential] = field(default_factory=list)
    pivot_capable: bool = False
    reachable_networks: List[str] = field(default_factory=list)
    compromised_at: datetime = field(default_factory=datetime.now)
    access_method: str = ""
    notes: str = ""

    def __hash__(self):
        """Hash based on IP address"""
        return hash(self.ip_address)

    def __eq__(self, other):
        """Equality based on IP address"""
        if not isinstance(other, CompromisedSystem):
            return False
        return self.ip_address == other.ip_address

    @property
    def is_windows(self) -> bool:
        """Check if system is Windows"""
        return self.platform == Platform.WINDOWS

    @property
    def is_linux(self) -> bool:
        """Check if system is Linux"""
        return self.platform == Platform.LINUX

    @property
    def has_elevated_access(self) -> bool:
        """Check if we have elevated privileges"""
        return self.privilege_level.is_elevated

    @property
    def credential_count(self) -> int:
        """Number of credentials harvested from this system"""
        return len(self.credentials_harvested)

    def add_credential(self, credential: Credential) -> bool:
        """
        Add a credential to this system's harvested list.
        Returns True if added (not duplicate), False otherwise.
        """
        if credential not in self.credentials_harvested:
            self.credentials_harvested.append(credential)
            return True
        return False

    def add_reachable_network(self, network: str) -> None:
        """Add a network to the reachable list"""
        if network not in self.reachable_networks:
            self.reachable_networks.append(network)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "platform": self.platform.value,
            "privilege_level": self.privilege_level.value,
            "credentials_harvested": [c.to_dict() for c in self.credentials_harvested],
            "pivot_capable": self.pivot_capable,
            "reachable_networks": self.reachable_networks,
            "compromised_at": self.compromised_at.isoformat(),
            "access_method": self.access_method,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CompromisedSystem":
        """Create CompromisedSystem from dictionary"""
        compromised_at = data.get("compromised_at")
        if isinstance(compromised_at, str):
            compromised_at = datetime.fromisoformat(compromised_at)
        elif compromised_at is None:
            compromised_at = datetime.now()

        credentials = [
            Credential.from_dict(c)
            for c in data.get("credentials_harvested", [])
        ]

        return cls(
            hostname=data.get("hostname", ""),
            ip_address=data.get("ip_address", ""),
            platform=Platform(data.get("platform", "windows")),
            privilege_level=PrivilegeLevel(data.get("privilege_level", "user")),
            credentials_harvested=credentials,
            pivot_capable=data.get("pivot_capable", False),
            reachable_networks=data.get("reachable_networks", []),
            compromised_at=compromised_at,
            access_method=data.get("access_method", ""),
            notes=data.get("notes", ""),
        )

    def __repr__(self):
        return (
            f"CompromisedSystem({self.hostname}, {self.ip_address}, "
            f"{self.platform.value}, {self.privilege_level.value})"
        )