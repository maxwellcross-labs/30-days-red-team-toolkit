"""
Enumerations for Week 3 Orchestrator
"""

from enum import Enum


class Platform(Enum):
    """Target operating system platform"""
    WINDOWS = "windows"
    LINUX = "linux"

    def __str__(self):
        return self.value


class PrivilegeLevel(Enum):
    """Privilege levels for compromised access"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    ROOT = "root"
    DOMAIN_ADMIN = "domain_admin"
    ENTERPRISE_ADMIN = "enterprise_admin"

    def __str__(self):
        return self.value

    @property
    def is_elevated(self) -> bool:
        """Check if this privilege level is elevated"""
        return self in (
            PrivilegeLevel.ADMIN,
            PrivilegeLevel.SYSTEM,
            PrivilegeLevel.ROOT,
            PrivilegeLevel.DOMAIN_ADMIN,
            PrivilegeLevel.ENTERPRISE_ADMIN,
        )

    @property
    def is_domain_level(self) -> bool:
        """Check if this is a domain-level privilege"""
        return self in (
            PrivilegeLevel.DOMAIN_ADMIN,
            PrivilegeLevel.ENTERPRISE_ADMIN,
        )