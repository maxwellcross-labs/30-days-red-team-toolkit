#!/usr/bin/env python3
"""
Initial Enumeration Module
Rapid situational awareness collection
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class EnumCommand:
    """Represents a single enumeration command"""
    category: str
    command: str
    description: str
    priority: int  # 1=critical, 2=important, 3=nice-to-have


class EnumerationManager:
    """
    Manages initial system enumeration
    Collects critical situational awareness data
    """
    
    def __init__(self, platform: str = "windows"):
        """
        Initialize enumeration manager
        
        Args:
            platform: Target platform ('windows' or 'linux')
        """
        self.platform = platform.lower()
        self.commands = self._initialize_commands()
    
    def _initialize_commands(self) -> List[EnumCommand]:
        """Initialize platform-specific enumeration commands"""
        if self.platform == "windows":
            return self._windows_commands()
        elif self.platform == "linux":
            return self._linux_commands()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _windows_commands(self) -> List[EnumCommand]:
        """Windows enumeration commands"""
        return [
            # Critical - Identity and Context
            EnumCommand(
                category="Identity",
                command="whoami",
                description="Current user context",
                priority=1
            ),
            EnumCommand(
                category="Identity",
                command="whoami /priv",
                description="Current user privileges",
                priority=1
            ),
            EnumCommand(
                category="Identity",
                command="whoami /groups",
                description="Current user group memberships",
                priority=1
            ),
            
            # Critical - System Information
            EnumCommand(
                category="System",
                command="hostname",
                description="System identification",
                priority=1
            ),
            EnumCommand(
                category="System",
                command="systeminfo",
                description="Detailed system information",
                priority=1
            ),
            
            # Critical - Network
            EnumCommand(
                category="Network",
                command="ipconfig /all",
                description="Network configuration",
                priority=1
            ),
            EnumCommand(
                category="Network",
                command="netstat -ano",
                description="Network connections and listening ports",
                priority=1
            ),
            
            # Important - Users and Groups
            EnumCommand(
                category="Users",
                command="net user",
                description="Local users",
                priority=2
            ),
            EnumCommand(
                category="Users",
                command="net localgroup administrators",
                description="Local administrators",
                priority=2
            ),
            EnumCommand(
                category="Users",
                command="net user /domain",
                description="Domain users (if domain-joined)",
                priority=2
            ),
            
            # Important - Processes and Services
            EnumCommand(
                category="Processes",
                command="tasklist /v",
                description="Running processes with details",
                priority=2
            ),
            EnumCommand(
                category="Services",
                command="sc query",
                description="Windows services",
                priority=2
            ),
            
            # Important - Security
            EnumCommand(
                category="Security",
                command="wmic qfe get Caption,Description,HotFixID,InstalledOn",
                description="Installed patches and updates",
                priority=2
            ),
            EnumCommand(
                category="Security",
                command="netsh firewall show state",
                description="Firewall status",
                priority=2
            ),
            EnumCommand(
                category="Security",
                command="netsh firewall show config",
                description="Firewall configuration",
                priority=2
            ),
            
            # Nice-to-have - Additional Context
            EnumCommand(
                category="Storage",
                command="wmic logicaldisk get caption,description,providername",
                description="Available drives",
                priority=3
            ),
            EnumCommand(
                category="Software",
                command="wmic product get name,version",
                description="Installed software",
                priority=3
            ),
            EnumCommand(
                category="Scheduled Tasks",
                command="schtasks /query /fo LIST",
                description="Scheduled tasks",
                priority=3
            )
        ]
    
    def _linux_commands(self) -> List[EnumCommand]:
        """Linux enumeration commands"""
        return [
            # Critical - Identity and Context
            EnumCommand(
                category="Identity",
                command="whoami",
                description="Current user context",
                priority=1
            ),
            EnumCommand(
                category="Identity",
                command="id",
                description="User ID and group memberships",
                priority=1
            ),
            
            # Critical - System Information
            EnumCommand(
                category="System",
                command="hostname",
                description="System identification",
                priority=1
            ),
            EnumCommand(
                category="System",
                command="uname -a",
                description="Kernel and system information",
                priority=1
            ),
            EnumCommand(
                category="System",
                command="cat /etc/os-release",
                description="Distribution information",
                priority=1
            ),
            
            # Critical - Network
            EnumCommand(
                category="Network",
                command="ip addr show",
                description="Network interfaces and addresses",
                priority=1
            ),
            EnumCommand(
                category="Network",
                command="netstat -tulpn",
                description="Network connections and listening ports",
                priority=1
            ),
            
            # Important - Users and Permissions
            EnumCommand(
                category="Users",
                command="cat /etc/passwd",
                description="System users",
                priority=2
            ),
            EnumCommand(
                category="Users",
                command="cat /etc/group",
                description="System groups",
                priority=2
            ),
            EnumCommand(
                category="Sudo",
                command="sudo -l",
                description="Sudo privileges",
                priority=2
            ),
            
            # Important - Processes
            EnumCommand(
                category="Processes",
                command="ps aux",
                description="Running processes",
                priority=2
            ),
            
            # Nice-to-have - Additional Context
            EnumCommand(
                category="Storage",
                command="df -h",
                description="Filesystem disk space",
                priority=3
            ),
            EnumCommand(
                category="Cron",
                command="crontab -l",
                description="User cron jobs",
                priority=3
            ),
            EnumCommand(
                category="Cron",
                command="cat /etc/crontab",
                description="System cron jobs",
                priority=3
            )
        ]
    
    def get_critical_commands(self) -> List[EnumCommand]:
        """Get priority 1 (critical) commands"""
        return [cmd for cmd in self.commands if cmd.priority == 1]
    
    def get_important_commands(self) -> List[EnumCommand]:
        """Get priority 2 (important) commands"""
        return [cmd for cmd in self.commands if cmd.priority == 2]
    
    def get_all_commands(self) -> List[EnumCommand]:
        """Get all enumeration commands"""
        return sorted(self.commands, key=lambda x: x.priority)
    
    def get_commands_by_category(self, category: str) -> List[EnumCommand]:
        """Get commands for specific category"""
        return [cmd for cmd in self.commands if cmd.category.lower() == category.lower()]
    
    def generate_command_list(self, priority_level: int = None) -> List[Tuple[str, str]]:
        """
        Generate list of commands for execution
        
        Args:
            priority_level: Filter by priority (1, 2, 3, or None for all)
            
        Returns:
            List of (command, description) tuples
        """
        if priority_level is None:
            commands = self.get_all_commands()
        else:
            commands = [cmd for cmd in self.commands if cmd.priority == priority_level]
        
        return [(cmd.command, cmd.description) for cmd in commands]
    
    def get_enumeration_checklist(self) -> Dict:
        """Generate enumeration checklist"""
        return {
            'platform': self.platform,
            'total_commands': len(self.commands),
            'by_priority': {
                'critical': len(self.get_critical_commands()),
                'important': len(self.get_important_commands()),
                'nice_to_have': len([cmd for cmd in self.commands if cmd.priority == 3])
            },
            'categories': list(set(cmd.category for cmd in self.commands))
        }
    
    def generate_batch_script(self, output_file: str = "enum_results.txt") -> str:
        """
        Generate batch script for automated enumeration
        
        Args:
            output_file: Output file for enumeration results
            
        Returns:
            Platform-specific script
        """
        if self.platform == "windows":
            return self._generate_windows_batch(output_file)
        else:
            return self._generate_linux_script(output_file)
    
    def _generate_windows_batch(self, output_file: str) -> str:
        """Generate Windows batch script"""
        script = f"@echo off\n"
        script += f"echo Initial Enumeration Results > {output_file}\n"
        script += f"echo ====================================== >> {output_file}\n"
        script += f"echo.\n\n"
        
        for cmd in self.get_all_commands():
            script += f"echo [*] {cmd.description}\n"
            script += f"echo. >> {output_file}\n"
            script += f"echo [{cmd.category}] {cmd.description} >> {output_file}\n"
            script += f"{cmd.command} >> {output_file} 2>&1\n"
            script += f"echo. >> {output_file}\n"
            script += f"echo ====================================== >> {output_file}\n\n"
        
        return script
    
    def _generate_linux_script(self, output_file: str) -> str:
        """Generate Linux bash script"""
        script = "#!/bin/bash\n\n"
        script += f"echo 'Initial Enumeration Results' > {output_file}\n"
        script += f"echo '======================================' >> {output_file}\n"
        script += f"echo '' >> {output_file}\n\n"
        
        for cmd in self.get_all_commands():
            script += f"echo '[*] {cmd.description}'\n"
            script += f"echo '' >> {output_file}\n"
            script += f"echo '[{cmd.category}] {cmd.description}' >> {output_file}\n"
            script += f"{cmd.command} >> {output_file} 2>&1\n"
            script += f"echo '' >> {output_file}\n"
            script += f"echo '======================================' >> {output_file}\n\n"
        
        return script
