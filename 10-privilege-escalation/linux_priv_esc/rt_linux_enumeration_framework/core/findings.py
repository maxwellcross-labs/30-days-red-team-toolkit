"""
Findings Model
==============

Data structures for privilege escalation findings with severity classification.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class FindingSeverity(Enum):
    """Severity classification for privilege escalation findings"""
    CRITICAL = "critical"  # Immediate privilege escalation possible
    HIGH = "high"  # High-probability exploitation path
    MEDIUM = "medium"  # Potential path requiring additional conditions
    LOW = "low"  # Complex or conditional exploitation
    INFO = "info"  # Informational finding


@dataclass
class Finding:
    """
    Represents a single privilege escalation finding.

    Attributes:
        category: Type of finding (e.g., 'SUID Binary', 'Writable Cron')
        severity: FindingSeverity classification
        finding: Human-readable description
        exploitation: How to exploit this finding
        impact: Expected impact upon exploitation
        target: Specific file/binary/resource affected
        metadata: Additional context-specific data
        timestamp: When the finding was discovered
    """
    category: str
    severity: FindingSeverity
    finding: str
    exploitation: str
    impact: str
    target: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for JSON serialization"""
        return {
            'category': self.category,
            'severity': self.severity.value,
            'finding': self.finding,
            'exploitation': self.exploitation,
            'impact': self.impact,
            'target': self.target,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Finding':
        """Create Finding from dictionary"""
        return cls(
            category=data['category'],
            severity=FindingSeverity(data['severity']),
            finding=data['finding'],
            exploitation=data['exploitation'],
            impact=data['impact'],
            target=data.get('target'),
            metadata=data.get('metadata', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now()
        )

    def __str__(self) -> str:
        """Pretty-print the finding"""
        return (
            f"[{self.severity.value.upper()}] {self.category}\n"
            f"  Target: {self.target or 'N/A'}\n"
            f"  Finding: {self.finding}\n"
            f"  Exploit: {self.exploitation}\n"
            f"  Impact: {self.impact}"
        )


class FindingsCollection:
    """
    Collection of privilege escalation findings with filtering and sorting.
    """

    def __init__(self):
        self._findings: List[Finding] = []

    def add(self, finding: Finding) -> None:
        """Add a finding to the collection"""
        self._findings.append(finding)

    def add_finding(
            self,
            category: str,
            severity: FindingSeverity,
            finding: str,
            exploitation: str,
            impact: str,
            target: Optional[str] = None,
            **metadata
    ) -> Finding:
        """Create and add a finding in one step"""
        new_finding = Finding(
            category=category,
            severity=severity,
            finding=finding,
            exploitation=exploitation,
            impact=impact,
            target=target,
            metadata=metadata
        )
        self._findings.append(new_finding)
        return new_finding

    def get_by_severity(self, severity: FindingSeverity) -> List[Finding]:
        """Get all findings of a specific severity"""
        return [f for f in self._findings if f.severity == severity]

    def get_critical(self) -> List[Finding]:
        """Get critical findings (exploit these first!)"""
        return self.get_by_severity(FindingSeverity.CRITICAL)

    def get_high(self) -> List[Finding]:
        """Get high-severity findings"""
        return self.get_by_severity(FindingSeverity.HIGH)

    def get_by_category(self, category: str) -> List[Finding]:
        """Get findings by category"""
        return [f for f in self._findings if f.category == category]

    def count_by_severity(self) -> Dict[str, int]:
        """Count findings by severity level"""
        return {
            'critical': len(self.get_by_severity(FindingSeverity.CRITICAL)),
            'high': len(self.get_by_severity(FindingSeverity.HIGH)),
            'medium': len(self.get_by_severity(FindingSeverity.MEDIUM)),
            'low': len(self.get_by_severity(FindingSeverity.LOW)),
            'info': len(self.get_by_severity(FindingSeverity.INFO))
        }

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all findings grouped by severity"""
        return {
            'critical': [f.to_dict() for f in self.get_critical()],
            'high': [f.to_dict() for f in self.get_high()],
            'medium': [f.to_dict() for f in self.get_by_severity(FindingSeverity.MEDIUM)],
            'low': [f.to_dict() for f in self.get_by_severity(FindingSeverity.LOW)],
            'info': [f.to_dict() for f in self.get_by_severity(FindingSeverity.INFO)]
        }

    def __len__(self) -> int:
        return len(self._findings)

    def __iter__(self):
        return iter(self._findings)

    @property
    def all(self) -> List[Finding]:
        """Get all findings"""
        return self._findings.copy()