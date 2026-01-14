#!/usr/bin/env python3
"""
Operation Logging
Comprehensive logging for post-engagement reporting
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class OperationLog:
    """
    Maintains detailed operation log for reporting and analysis
    Every action, result, and timestamp documented
    """
    
    def __init__(self, session_id: str, log_dir: Optional[str] = None):
        """
        Initialize operation logging
        
        Args:
            session_id: Unique session identifier
            log_dir: Directory for log storage (default: /tmp)
        """
        self.session_id = session_id
        self.log_dir = Path(log_dir or "/tmp")
        self.log_entries: List[Dict] = []
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_action(self, action: str, status: str, details: str = "") -> None:
        """
        Log a single operation action
        
        Args:
            action: Action being performed (e.g., "Persistence", "C2 Setup")
            status: Status of action (e.g., "SUCCESS", "FAILED", "Starting")
            details: Additional context or error information
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        
        self.log_entries.append(entry)
        
        # Real-time console output
        print(f"[{entry['timestamp']}] {action}: {status}")
        if details:
            print(f"    └─ {details}")
    
    def log_phase_start(self, phase: str, description: str = "") -> None:
        """Log the start of a major operational phase"""
        print("\n" + "="*60)
        print(f"PHASE: {phase.upper()}")
        if description:
            print(f"└─ {description}")
        print("="*60)
        
        self.log_action(phase, "STARTING", description)
    
    def log_phase_complete(self, phase: str, summary: str = "") -> None:
        """Log completion of a major operational phase"""
        self.log_action(phase, "COMPLETE", summary)
        print(f"\n✓ {phase} Complete")
        if summary:
            print(f"  {summary}")
    
    def get_logs(self) -> List[Dict]:
        """Retrieve all log entries"""
        return self.log_entries
    
    def get_logs_by_action(self, action: str) -> List[Dict]:
        """Get all log entries for a specific action"""
        return [entry for entry in self.log_entries if entry['action'] == action]
    
    def get_logs_by_status(self, status: str) -> List[Dict]:
        """Get all log entries with specific status"""
        return [entry for entry in self.log_entries if entry['status'] == status]
    
    def save_log(self, filename: Optional[str] = None) -> Path:
        """
        Save operation log to JSON file
        
        Args:
            filename: Custom filename (default: session_id_operation_log.json)
            
        Returns:
            Path to saved log file
        """
        if filename is None:
            filename = f"{self.session_id}_operation_log.json"
        
        log_path = self.log_dir / filename
        
        with open(log_path, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'log_entries': self.log_entries,
                'summary': {
                    'total_actions': len(self.log_entries),
                    'successful': len(self.get_logs_by_status('SUCCESS')),
                    'failed': len(self.get_logs_by_status('FAILED')),
                    'errors': len(self.get_logs_by_status('ERROR'))
                }
            }, f, indent=2)
        
        self.log_action("Logging", "SUCCESS", f"Operation log saved: {log_path}")
        return log_path
    
    def generate_report(self) -> str:
        """Generate human-readable operation report"""
        successful = len(self.get_logs_by_status('SUCCESS'))
        failed = len(self.get_logs_by_status('FAILED'))
        errors = len(self.get_logs_by_status('ERROR'))
        
        report = f"""
{'='*60}
OPERATION REPORT - {self.session_id}
{'='*60}

Total Actions: {len(self.log_entries)}
Successful: {successful}
Failed: {failed}
Errors: {errors}

{'='*60}
DETAILED LOG
{'='*60}
"""
        
        for entry in self.log_entries:
            report += f"\n[{entry['timestamp']}]"
            report += f"\n  Action: {entry['action']}"
            report += f"\n  Status: {entry['status']}"
            if entry['details']:
                report += f"\n  Details: {entry['details']}"
            report += "\n"
        
        return report
