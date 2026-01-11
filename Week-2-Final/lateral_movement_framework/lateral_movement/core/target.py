#!/usr/bin/env python3
"""
Target Management
Represents and tracks individual target systems
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List


@dataclass
class Target:
    """
    Represents a single target system for lateral movement
    """
    hostname: str
    ip_address: str
    status: str = "pending"  # pending, testing, compromised, failed
    os_type: str = "windows"
    open_ports: List[int] = field(default_factory=list)
    
    # Compromise details
    compromised: bool = False
    compromise_method: Optional[str] = None
    compromise_time: Optional[datetime] = None
    used_credential: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def __post_init__(self):
        """Validate target data"""
        if not self.hostname and not self.ip_address:
            raise ValueError("Target must have either hostname or IP address")
    
    def mark_compromised(self, method: str, credential: str) -> None:
        """
        Mark target as successfully compromised
        
        Args:
            method: Authentication method used
            credential: Credential used for access
        """
        self.compromised = True
        self.status = "compromised"
        self.compromise_method = method
        self.compromise_time = datetime.now()
        self.used_credential = credential
    
    def mark_failed(self) -> None:
        """Mark target as failed compromise attempt"""
        self.status = "failed"
        self.compromised = False
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the target"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def get_identifier(self) -> str:
        """Get primary identifier for target"""
        return self.hostname if self.hostname else self.ip_address
    
    def to_dict(self) -> Dict:
        """Convert target to dictionary"""
        return {
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'status': self.status,
            'os_type': self.os_type,
            'open_ports': self.open_ports,
            'compromised': self.compromised,
            'compromise_method': self.compromise_method,
            'compromise_time': self.compromise_time.isoformat() if self.compromise_time else None,
            'used_credential': self.used_credential,
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Target':
        """Create Target from dictionary"""
        target = cls(
            hostname=data.get('hostname', ''),
            ip_address=data.get('ip_address', ''),
            status=data.get('status', 'pending'),
            os_type=data.get('os_type', 'windows'),
            open_ports=data.get('open_ports', [])
        )
        
        target.compromised = data.get('compromised', False)
        target.compromise_method = data.get('compromise_method')
        
        if data.get('compromise_time'):
            target.compromise_time = datetime.fromisoformat(data['compromise_time'])
        
        target.used_credential = data.get('used_credential')
        target.tags = data.get('tags', [])
        target.notes = data.get('notes', '')
        
        return target
