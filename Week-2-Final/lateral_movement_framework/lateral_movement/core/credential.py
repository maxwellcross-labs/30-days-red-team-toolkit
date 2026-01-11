#!/usr/bin/env python3
"""
Credential Management
Represents and tracks credentials for lateral movement
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Credential:
    """
    Represents a credential pair for authentication
    """
    username: str
    password: str
    domain: Optional[str] = None
    credential_type: str = "password"  # password, hash, ticket
    
    # Tracking
    successful_targets: List[str] = field(default_factory=list)
    failed_targets: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    
    # Metadata
    source: str = "unknown"  # harvest, breach, social_engineering, etc.
    privilege_level: str = "user"  # user, admin, domain_admin
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def get_identifier(self) -> str:
        """Get unique identifier for credential"""
        if self.domain:
            return f"{self.domain}\\{self.username}"
        return self.username
    
    def mark_successful(self, target: str) -> None:
        """
        Mark credential as successful against target
        
        Args:
            target: Target identifier
        """
        if target not in self.successful_targets:
            self.successful_targets.append(target)
        self.last_used = datetime.now()
    
    def mark_failed(self, target: str) -> None:
        """
        Mark credential as failed against target
        
        Args:
            target: Target identifier
        """
        if target not in self.failed_targets:
            self.failed_targets.append(target)
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = len(self.successful_targets) + len(self.failed_targets)
        if total == 0:
            return 0.0
        return (len(self.successful_targets) / total) * 100
    
    def is_high_value(self) -> bool:
        """Determine if credential is high-value"""
        return (
            self.privilege_level in ['admin', 'domain_admin'] or
            len(self.successful_targets) >= 3 or
            'high_value' in self.tags
        )
    
    def to_dict(self) -> Dict:
        """Convert credential to dictionary"""
        return {
            'username': self.username,
            'password': '***REDACTED***',  # Never expose password in exports
            'domain': self.domain,
            'credential_type': self.credential_type,
            'successful_targets': self.successful_targets,
            'failed_targets': self.failed_targets,
            'first_seen': self.first_seen.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'source': self.source,
            'privilege_level': self.privilege_level,
            'success_rate': f"{self.get_success_rate():.1f}%",
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_tuple(cls, cred_tuple: tuple, domain: str = None, source: str = "unknown") -> 'Credential':
        """
        Create Credential from tuple (username, password)
        
        Args:
            cred_tuple: Tuple of (username, password)
            domain: Optional domain
            source: Source of credential
            
        Returns:
            Credential object
        """
        username, password = cred_tuple
        return cls(
            username=username,
            password=password,
            domain=domain,
            source=source
        )
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Credential':
        """Create Credential from dictionary"""
        cred = cls(
            username=data['username'],
            password=data.get('password', ''),  # May be redacted
            domain=data.get('domain'),
            credential_type=data.get('credential_type', 'password'),
            source=data.get('source', 'unknown'),
            privilege_level=data.get('privilege_level', 'user'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )
        
        cred.successful_targets = data.get('successful_targets', [])
        cred.failed_targets = data.get('failed_targets', [])
        
        if data.get('first_seen'):
            cred.first_seen = datetime.fromisoformat(data['first_seen'])
        
        if data.get('last_used'):
            cred.last_used = datetime.fromisoformat(data['last_used'])
        
        return cred
