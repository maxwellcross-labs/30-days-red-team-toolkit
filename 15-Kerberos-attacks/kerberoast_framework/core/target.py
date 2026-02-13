"""
RoastingTarget — Data model for roastable Active Directory accounts.

Represents a Kerberoastable or AS-REP Roastable account with
priority scoring based on privilege level and description keywords.
"""

from typing import List


class RoastingTarget:
    """Represents a roastable account discovered via LDAP enumeration."""

    PRIORITY_KEYWORDS = ['admin', 'prod', 'sql', 'backup']

    def __init__(
        self,
        username: str,
        domain: str,
        spns: List[str] = None,
        is_admin: bool = False,
        description: str = "",
        pwd_last_set: str = "",
        roast_type: str = "kerberoast",
    ):
        self.username = username
        self.domain = domain
        self.spns = spns or []
        self.is_admin = is_admin
        self.description = description
        self.pwd_last_set = pwd_last_set
        self.roast_type = roast_type
        self.hash_value = ""
        self.cracked_password = ""

    @property
    def priority(self) -> str:
        """Score target priority: CRITICAL > HIGH > MEDIUM."""
        if self.is_admin:
            return "CRITICAL"
        if any(kw in self.description.lower() for kw in self.PRIORITY_KEYWORDS):
            return "HIGH"
        return "MEDIUM"

    @property
    def priority_icon(self) -> str:
        return {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🟢"}.get(self.priority, "")

    def __repr__(self):
        return (
            f"<RoastingTarget {self.domain}\\{self.username} "
            f"[{self.roast_type}] [{self.priority}]>"
        )