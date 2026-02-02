"""
Attack State Model
==================

Tracks the overall state of the attack operation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime

from .credential import Credential
from .system import CompromisedSystem


@dataclass
class AttackState:
    """
    Tracks the current state of the attack operation.

    Attributes:
        initial_system: The first compromised system (entry point)
        compromised_systems: All systems compromised during operation
        all_credentials: All credentials harvested across all systems
        active_pivots: Currently active pivot/tunnel configurations
        compromised_domains: Domains where we have admin access
        trust_relationships: Discovered trust relationships
        operation_start: When the operation began
        current_phase: Current phase of the attack chain
    """
    initial_system: Optional[CompromisedSystem] = None
    compromised_systems: List[CompromisedSystem] = field(default_factory=list)
    all_credentials: List[Credential] = field(default_factory=list)
    active_pivots: List[Dict] = field(default_factory=list)
    compromised_domains: List[str] = field(default_factory=list)
    trust_relationships: List[Dict] = field(default_factory=list)
    operation_start: datetime = field(default_factory=datetime.now)
    current_phase: int = 0

    @property
    def system_count(self) -> int:
        """Number of compromised systems"""
        return len(self.compromised_systems)

    @property
    def credential_count(self) -> int:
        """Total unique credentials"""
        return len(self.all_credentials)

    @property
    def domain_count(self) -> int:
        """Number of compromised domains"""
        return len(self.compromised_domains)

    @property
    def pivot_count(self) -> int:
        """Number of active pivots"""
        return len(self.active_pivots)

    def add_system(self, system: CompromisedSystem) -> bool:
        """
        Add a compromised system to the state.
        Returns True if added (not duplicate), False otherwise.
        """
        if system not in self.compromised_systems:
            self.compromised_systems.append(system)
            return True
        return False

    def add_credential(self, credential: Credential) -> bool:
        """
        Add a credential to the global list.
        Returns True if added (not duplicate), False otherwise.
        """
        if credential not in self.all_credentials:
            self.all_credentials.append(credential)
            return True
        return False

    def add_credentials(self, credentials: List[Credential]) -> int:
        """
        Add multiple credentials.
        Returns count of new credentials added.
        """
        added = 0
        for cred in credentials:
            if self.add_credential(cred):
                added += 1
        return added

    def add_pivot(self, pivot_config: Dict) -> None:
        """Add an active pivot configuration"""
        self.active_pivots.append(pivot_config)

    def add_domain(self, domain: str) -> bool:
        """
        Add a compromised domain.
        Returns True if added (not duplicate), False otherwise.
        """
        domain_lower = domain.lower()
        if domain_lower not in [d.lower() for d in self.compromised_domains]:
            self.compromised_domains.append(domain)
            return True
        return False

    def add_trust(self, trust_info: Dict) -> None:
        """Add a discovered trust relationship"""
        self.trust_relationships.append(trust_info)

    def get_system_by_ip(self, ip: str) -> Optional[CompromisedSystem]:
        """Find a compromised system by IP address"""
        for system in self.compromised_systems:
            if system.ip_address == ip:
                return system
        return None

    def get_system_by_hostname(self, hostname: str) -> Optional[CompromisedSystem]:
        """Find a compromised system by hostname"""
        hostname_lower = hostname.lower()
        for system in self.compromised_systems:
            if system.hostname.lower() == hostname_lower:
                return system
        return None

    def get_credentials_by_privilege(self, privilege: str) -> List[Credential]:
        """Get all credentials with a specific privilege level"""
        return [
            c for c in self.all_credentials
            if c.privilege_level.lower() == privilege.lower()
        ]

    def get_domain_admin_credentials(self) -> List[Credential]:
        """Get all domain admin credentials"""
        return self.get_credentials_by_privilege("domain_admin")

    def get_pivot_capable_systems(self) -> List[CompromisedSystem]:
        """Get all systems that can be used as pivots"""
        return [s for s in self.compromised_systems if s.pivot_capable]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "initial_system": self.initial_system.to_dict() if self.initial_system else None,
            "compromised_systems": [s.to_dict() for s in self.compromised_systems],
            "all_credentials": [c.to_dict() for c in self.all_credentials],
            "active_pivots": self.active_pivots,
            "compromised_domains": self.compromised_domains,
            "trust_relationships": self.trust_relationships,
            "operation_start": self.operation_start.isoformat(),
            "current_phase": self.current_phase,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AttackState":
        """Create AttackState from dictionary"""
        initial = data.get("initial_system")
        if initial:
            initial = CompromisedSystem.from_dict(initial)

        systems = [
            CompromisedSystem.from_dict(s)
            for s in data.get("compromised_systems", [])
        ]

        credentials = [
            Credential.from_dict(c)
            for c in data.get("all_credentials", [])
        ]

        operation_start = data.get("operation_start")
        if isinstance(operation_start, str):
            operation_start = datetime.fromisoformat(operation_start)
        elif operation_start is None:
            operation_start = datetime.now()

        return cls(
            initial_system=initial,
            compromised_systems=systems,
            all_credentials=credentials,
            active_pivots=data.get("active_pivots", []),
            compromised_domains=data.get("compromised_domains", []),
            trust_relationships=data.get("trust_relationships", []),
            operation_start=operation_start,
            current_phase=data.get("current_phase", 0),
        )

    def summary(self) -> str:
        """Generate a text summary of the current state"""
        return f"""
Attack State Summary
====================
Operation Start: {self.operation_start.strftime("%Y-%m-%d %H:%M:%S")}
Current Phase: {self.current_phase}

Systems Compromised: {self.system_count}
Credentials Harvested: {self.credential_count}
Active Pivots: {self.pivot_count}
Domains Compromised: {self.domain_count}
Trust Relationships: {len(self.trust_relationships)}
"""