#!/usr/bin/env python3
"""
Session Management
Tracks operation session state and metadata
"""

import time
from datetime import datetime
from typing import Dict, Optional


class Session:
    """
    Represents a single red team operation session
    Maintains state, timing, and target information
    """
    
    def __init__(self, target_ip: str, c2_server: str, session_name: Optional[str] = None):
        """
        Initialize operation session
        
        Args:
            target_ip: Target system IP address
            c2_server: Command and Control server address
            session_name: Optional custom session identifier
        """
        self.target_ip = target_ip
        self.c2_server = c2_server
        self.session_id = session_name or f"session_{int(time.time())}"
        self.start_time = datetime.now()
        self.end_time = None
        
        # Session state tracking
        self.access_verified = False
        self.persistence_installed = False
        self.c2_established = False
        self.enumeration_complete = False
        self.cleanup_configured = False
        
        # Metadata
        self.metadata = {
            'target': target_ip,
            'c2': c2_server,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat()
        }
    
    def mark_phase_complete(self, phase: str) -> None:
        """Mark operational phase as complete"""
        phase_mapping = {
            'access': 'access_verified',
            'persistence': 'persistence_installed',
            'c2': 'c2_established',
            'enumeration': 'enumeration_complete',
            'cleanup': 'cleanup_configured'
        }
        
        if phase in phase_mapping:
            setattr(self, phase_mapping[phase], True)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds since session start"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_elapsed_time_formatted(self) -> str:
        """Get human-readable elapsed time"""
        seconds = self.get_elapsed_time()
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    
    def get_session_status(self) -> Dict:
        """Get complete session status"""
        return {
            'session_id': self.session_id,
            'target': self.target_ip,
            'c2_server': self.c2_server,
            'elapsed_time': self.get_elapsed_time_formatted(),
            'phases': {
                'access_verified': self.access_verified,
                'persistence_installed': self.persistence_installed,
                'c2_established': self.c2_established,
                'enumeration_complete': self.enumeration_complete,
                'cleanup_configured': self.cleanup_configured
            }
        }
    
    def finalize(self) -> None:
        """Mark session as complete"""
        self.end_time = datetime.now()
        self.metadata['end_time'] = self.end_time.isoformat()
        self.metadata['total_duration'] = self.get_elapsed_time_formatted()
