#!/usr/bin/env python3
"""
Campaign Management
Tracks complete lateral movement campaign state
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from .target import Target
from .credential import Credential


class Campaign:
    """
    Manages a complete lateral movement campaign
    Tracks targets, credentials, and compromise status
    """
    
    def __init__(self, campaign_id: str, targets: List[Target] = None, credentials: List[Credential] = None):
        """
        Initialize campaign
        
        Args:
            campaign_id: Unique campaign identifier
            targets: List of Target objects
            credentials: List of Credential objects
        """
        self.campaign_id = campaign_id
        self.targets = targets or []
        self.credentials = credentials or []
        
        self.start_time = datetime.now()
        self.end_time = None
        
        # Statistics
        self.total_attempts = 0
        self.successful_compromises = 0
        self.failed_attempts = 0
    
    def add_target(self, target: Target) -> None:
        """Add target to campaign"""
        self.targets.append(target)
    
    def add_credential(self, credential: Credential) -> None:
        """Add credential to campaign"""
        self.credentials.append(credential)
    
    def get_pending_targets(self) -> List[Target]:
        """Get all targets that haven't been attempted"""
        return [t for t in self.targets if t.status == 'pending']
    
    def get_compromised_targets(self) -> List[Target]:
        """Get all successfully compromised targets"""
        return [t for t in self.targets if t.compromised]
    
    def get_failed_targets(self) -> List[Target]:
        """Get all targets that failed compromise"""
        return [t for t in self.targets if t.status == 'failed']
    
    def get_high_value_credentials(self) -> List[Credential]:
        """Get high-value credentials"""
        return [c for c in self.credentials if c.is_high_value()]
    
    def record_attempt(self, target: Target, credential: Credential, success: bool) -> None:
        """
        Record a lateral movement attempt
        
        Args:
            target: Target that was attempted
            credential: Credential that was used
            success: Whether attempt was successful
        """
        self.total_attempts += 1
        
        if success:
            self.successful_compromises += 1
            credential.mark_successful(target.get_identifier())
        else:
            self.failed_attempts += 1
            credential.mark_failed(target.get_identifier())
    
    def get_success_rate(self) -> float:
        """Calculate overall campaign success rate"""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_compromises / self.total_attempts) * 100
    
    def get_statistics(self) -> Dict:
        """Get comprehensive campaign statistics"""
        return {
            'campaign_id': self.campaign_id,
            'total_targets': len(self.targets),
            'pending_targets': len(self.get_pending_targets()),
            'compromised_targets': len(self.get_compromised_targets()),
            'failed_targets': len(self.get_failed_targets()),
            'total_credentials': len(self.credentials),
            'high_value_credentials': len(self.get_high_value_credentials()),
            'total_attempts': self.total_attempts,
            'successful_compromises': self.successful_compromises,
            'failed_attempts': self.failed_attempts,
            'success_rate': f"{self.get_success_rate():.1f}%",
            'elapsed_time': self.get_elapsed_time()
        }
    
    def get_elapsed_time(self) -> str:
        """Get elapsed time since campaign start"""
        if self.end_time:
            delta = self.end_time - self.start_time
        else:
            delta = datetime.now() - self.start_time
        
        seconds = int(delta.total_seconds())
        minutes = seconds // 60
        hours = minutes // 60
        
        if hours > 0:
            return f"{hours}h {minutes % 60}m"
        elif minutes > 0:
            return f"{minutes}m {seconds % 60}s"
        else:
            return f"{seconds}s"
    
    def finalize(self) -> None:
        """Mark campaign as complete"""
        self.end_time = datetime.now()
    
    def save_to_file(self, output_path: Path) -> None:
        """
        Save campaign to JSON file
        
        Args:
            output_path: Path to save campaign data
        """
        campaign_data = {
            'campaign_id': self.campaign_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'statistics': self.get_statistics(),
            'targets': [t.to_dict() for t in self.targets],
            'credentials': [c.to_dict() for c in self.credentials]
        }
        
        with open(output_path, 'w') as f:
            json.dump(campaign_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, input_path: Path) -> 'Campaign':
        """
        Load campaign from JSON file
        
        Args:
            input_path: Path to campaign file
            
        Returns:
            Campaign object
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        campaign = cls(campaign_id=data['campaign_id'])
        
        # Load targets
        for target_data in data.get('targets', []):
            campaign.add_target(Target.from_dict(target_data))
        
        # Load credentials (passwords will be redacted)
        for cred_data in data.get('credentials', []):
            campaign.add_credential(Credential.from_dict(cred_data))
        
        if data.get('start_time'):
            campaign.start_time = datetime.fromisoformat(data['start_time'])
        
        if data.get('end_time'):
            campaign.end_time = datetime.fromisoformat(data['end_time'])
        
        return campaign
    
    def generate_report(self) -> str:
        """Generate human-readable campaign report"""
        stats = self.get_statistics()
        
        report = f"""
{'='*60}
LATERAL MOVEMENT CAMPAIGN REPORT
Campaign: {self.campaign_id}
{'='*60}

OVERVIEW
Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {stats['elapsed_time']}
Success Rate: {stats['success_rate']}

TARGETS
Total: {stats['total_targets']}
Compromised: {stats['compromised_targets']}
Failed: {stats['failed_targets']}
Pending: {stats['pending_targets']}

CREDENTIALS
Total: {stats['total_credentials']}
High-Value: {stats['high_value_credentials']}

ATTEMPTS
Total: {stats['total_attempts']}
Successful: {stats['successful_compromises']}
Failed: {stats['failed_attempts']}

"""
        
        # Compromised targets
        compromised = self.get_compromised_targets()
        if compromised:
            report += f"COMPROMISED TARGETS ({len(compromised)})\n"
            report += "="*60 + "\n"
            for target in compromised:
                report += f"\n  • {target.get_identifier()}\n"
                report += f"    Method: {target.compromise_method}\n"
                report += f"    Credential: {target.used_credential}\n"
                report += f"    Time: {target.compromise_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # High-value credentials
        high_value = self.get_high_value_credentials()
        if high_value:
            report += f"\n\nHIGH-VALUE CREDENTIALS ({len(high_value)})\n"
            report += "="*60 + "\n"
            for cred in high_value:
                report += f"\n  • {cred.get_identifier()}\n"
                report += f"    Privilege: {cred.privilege_level}\n"
                report += f"    Success Rate: {cred.get_success_rate():.1f}%\n"
                report += f"    Successful Targets: {len(cred.successful_targets)}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
