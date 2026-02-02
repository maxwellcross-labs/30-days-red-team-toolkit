"""
Credential Model
================

Represents harvested credentials from compromised systems.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Credential:
    """
    Represents a harvested credential.

    Attributes:
        username: The username/account name
        domain: Domain name (empty for local accounts)
        password: Plaintext password (if available)
        ntlm_hash: NT hash (if available)
        aes_key: AES256 key for Kerberos (if available)
        source: Where this credential was harvested from
        privilege_level: Known privilege level of this account
        harvested_at: Timestamp when credential was harvested
        verified: Whether credential has been tested/verified
    """
    username: str
    domain: str = ""
    password: str = ""
    ntlm_hash: str = ""
    aes_key: str = ""
    source: str = ""
    privilege_level: str = ""
    harvested_at: datetime = field(default_factory=datetime.now)
    verified: bool = False

    def __hash__(self):
        """Hash based on username and domain for deduplication"""
        return hash((self.username.lower(), self.domain.lower()))

    def __eq__(self, other):
        """Equality based on username and domain"""
        if not isinstance(other, Credential):
            return False
        return (
                self.username.lower() == other.username.lower() and
                self.domain.lower() == other.domain.lower()
        )

    @property
    def full_username(self) -> str:
        """Return domain\\username format"""
        if self.domain:
            return f"{self.domain}\\{self.username}"
        return self.username

    @property
    def has_password(self) -> bool:
        """Check if plaintext password is available"""
        return bool(self.password)

    @property
    def has_hash(self) -> bool:
        """Check if NTLM hash is available"""
        return bool(self.ntlm_hash)

    @property
    def has_aes_key(self) -> bool:
        """Check if AES key is available"""
        return bool(self.aes_key)

    @property
    def is_usable(self) -> bool:
        """Check if credential has usable authentication material"""
        return self.has_password or self.has_hash or self.has_aes_key

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "username": self.username,
            "domain": self.domain,
            "password": self.password,
            "ntlm_hash": self.ntlm_hash,
            "aes_key": self.aes_key,
            "source": self.source,
            "privilege_level": self.privilege_level,
            "harvested_at": self.harvested_at.isoformat(),
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Credential":
        """Create Credential from dictionary"""
        harvested_at = data.get("harvested_at")
        if isinstance(harvested_at, str):
            harvested_at = datetime.fromisoformat(harvested_at)
        elif harvested_at is None:
            harvested_at = datetime.now()

        return cls(
            username=data.get("username", ""),
            domain=data.get("domain", ""),
            password=data.get("password", ""),
            ntlm_hash=data.get("ntlm_hash", ""),
            aes_key=data.get("aes_key", ""),
            source=data.get("source", ""),
            privilege_level=data.get("privilege_level", ""),
            harvested_at=harvested_at,
            verified=data.get("verified", False),
        )

    def __repr__(self):
        cred_type = []
        if self.has_password:
            cred_type.append("password")
        if self.has_hash:
            cred_type.append("hash")
        if self.has_aes_key:
            cred_type.append("aes")

        return f"Credential({self.full_username}, types=[{', '.join(cred_type)}])"