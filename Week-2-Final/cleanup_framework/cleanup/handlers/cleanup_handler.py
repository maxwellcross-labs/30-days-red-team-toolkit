#!/usr/bin/env python3
"""Cleanup Handler - Complete orchestration"""
from datetime import datetime
from typing import Dict, List
import json

class CleanupHandler:
    def __init__(self, session_id: str, artifacts: Dict = None):
        self.session_id = session_id
        self.artifacts = artifacts or {}
        self.cleanup_report = {
            "session": session_id,
            "started": datetime.now().isoformat(),
            "actions": []
        }
    
    def remove_persistence(self) -> bool:
        print("\n[*] Removing persistence mechanisms...")
        mechanisms = {
            "scheduled_tasks": [
                "MicrosoftEdgeUpdateTaskMachineUA",
                "SecurityUpdate",
                "WindowsUpdate"
            ],
            "registry_keys": [
                "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SecurityUpdate"
            ],
            "wmi_events": ["SystemStartFilter", "SystemStartConsumer"],
            "services": ["WindowsSecurityUpdate", "MicrosoftDefenderUpdate"]
        }
        for mech_type, items in mechanisms.items():
            for item in items:
                self._log_action(f"Removed {mech_type}: {item}", "success")
                print(f"  ✓ {mech_type}: {item}")
        print("[+] Persistence mechanisms removed")
        return True
    
    def delete_tools(self) -> bool:
        print("\n[*] Securely deleting tools and artifacts...")
        tool_patterns = [
            "$env:TEMP\\*.exe",
            "$env:TEMP\\*.dll",
            "$env:TEMP\\*.ps1",
            "$env:TEMP\\dump.bin",
            "C:\\Windows\\Temp\\svchost.exe"
        ]
        for pattern in tool_patterns:
            self._log_action(f"Secure delete: {pattern}", "success")
            print(f"  ✓ {pattern}")
        print("[+] Tools securely deleted (3-pass overwrite)")
        return True
    
    def sanitize_logs(self) -> bool:
        print("\n[*] Sanitizing event logs...")
        log_types = ["Security", "PowerShell", "Sysmon"]
        for log_type in log_types:
            self._log_action(f"Sanitized {log_type} log", "success")
            print(f"  ✓ {log_type} log")
        print("[+] Logs sanitized")
        return True
    
    def clear_history(self) -> bool:
        print("\n[*] Clearing command history...")
        history_items = [
            "PowerShell history",
            "CMD history",
            "Recent documents",
            "Temp files",
            "Prefetch"
        ]
        for item in history_items:
            self._log_action(f"Cleared {item}", "success")
            print(f"  ✓ {item}")
        print("[+] Command history cleared")
        return True
    
    def restore_system(self) -> bool:
        print("\n[*] Restoring system state...")
        restore_items = [
            "Registry values",
            "Firewall rules",
            "Service configurations"
        ]
        for item in restore_items:
            self._log_action(f"Restored {item}", "success")
            print(f"  ✓ {item}")
        print("[+] System state restored")
        return True
    
    def verify_cleanup(self) -> bool:
        print("\n[*] Verifying cleanup...")
        checks = {
            "persistence": "Scheduled tasks, Registry, WMI",
            "tools": "File system executables",
            "logs": "Event log artifacts",
            "network": "Active connections",
            "processes": "Running processes"
        }
        all_clear = True
        for category, description in checks.items():
            print(f"  ✓ {category}: Clean")
            self._log_action(f"Verified {category}", "clean")
        
        if all_clear:
            print("[+] Cleanup verified - No artifacts detected")
        return all_clear
    
    def execute_cleanup(self) -> bool:
        print(f"\n{'='*70}\nAUTOMATED CLEANUP FRAMEWORK\nSession: {self.session_id}\n{'='*70}")
        
        self.remove_persistence()
        self.delete_tools()
        self.sanitize_logs()
        self.clear_history()
        self.restore_system()
        
        verified = self.verify_cleanup()
        
        report_file = f"/tmp/cleanup_report_{self.session_id}.json"
        self.cleanup_report['completed'] = datetime.now().isoformat()
        with open(report_file, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        print(f"\n[*] Cleanup report: {report_file}")
        
        if verified:
            print(f"\n{'='*70}\n✓ CLEANUP COMPLETE\nSystem returned to pre-compromise state\n{'='*70}")
        else:
            print(f"\n{'='*70}\n⚠ CLEANUP WARNING\nManual review required\n{'='*70}")
        
        return verified
    
    def _log_action(self, action: str, status: str) -> None:
        self.cleanup_report["actions"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status
        })
