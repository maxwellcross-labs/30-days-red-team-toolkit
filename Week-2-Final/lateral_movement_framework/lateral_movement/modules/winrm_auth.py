#!/usr/bin/env python3
"""
WinRM Authentication Module
Tests Windows Remote Management authentication
"""

import subprocess
from typing import Tuple, Optional


class WinRMAuthenticator:
    """
    Windows Remote Management authentication testing
    Uses evil-winrm or PowerShell remoting
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize WinRM authenticator
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
        self.method_name = "WinRM"
        self.default_port = 5985  # HTTP
        self.ssl_port = 5986      # HTTPS
    
    def test_authentication(self, target: str, username: str, password: str, 
                          domain: str = None, use_ssl: bool = False) -> Tuple[bool, str]:
        """
        Test WinRM authentication against target
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            domain: Optional domain
            use_ssl: Use HTTPS (port 5986) instead of HTTP (port 5985)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try evil-winrm first
            success, msg = self._test_evil_winrm(target, username, password, domain, use_ssl)
            if success:
                return success, msg
            
            # Fallback to PowerShell if evil-winrm not available
            return self._test_powershell(target, username, password, domain, use_ssl)
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _test_evil_winrm(self, target: str, username: str, password: str,
                        domain: str = None, use_ssl: bool = False) -> Tuple[bool, str]:
        """
        Test using evil-winrm
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Build username with domain if provided
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            cmd = [
                "evil-winrm",
                "-i", target,
                "-u", user_string,
                "-p", password,
                "-e", "exit"  # Exit immediately after connection test
            ]
            
            if use_ssl:
                cmd.append("-s")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            # evil-winrm doesn't have auth-only mode, so check for successful connection
            if "shell" in result.stdout.lower() or "PS " in result.stdout:
                return True, "WinRM authentication successful"
            elif "unauthorized" in result.stderr.lower() or "401" in result.stderr:
                return False, "Invalid credentials"
            elif "connection refused" in result.stderr.lower():
                return False, "WinRM port closed or filtered"
            else:
                return False, "WinRM connection failed"
        
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except FileNotFoundError:
            # evil-winrm not found, will try PowerShell
            return False, "evil-winrm not installed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _test_powershell(self, target: str, username: str, password: str,
                        domain: str = None, use_ssl: bool = False) -> Tuple[bool, str]:
        """
        Test using PowerShell remoting
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            # PowerShell script to test WinRM
            ps_script = f"""
$password = ConvertTo-SecureString '{password}' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('{user_string}', $password)

try {{
    $session = New-PSSession -ComputerName {target} -Credential $cred -ErrorAction Stop
    if ($session) {{
        Remove-PSSession $session
        Write-Output "SUCCESS"
    }}
}} catch {{
    Write-Error $_.Exception.Message
}}
"""
            
            cmd = ["powershell", "-Command", ps_script]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if "SUCCESS" in result.stdout:
                return True, "WinRM authentication successful"
            elif "Access is denied" in result.stderr or "authentication" in result.stderr.lower():
                return False, "Invalid credentials"
            else:
                return False, "WinRM connection failed"
        
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except FileNotFoundError:
            return False, "PowerShell not available"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def execute_command(self, target: str, username: str, password: str,
                       command: str, domain: str = None) -> Tuple[bool, str]:
        """
        Execute command via WinRM
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            command: Command to execute
            domain: Optional domain
            
        Returns:
            Tuple of (success, output)
        """
        try:
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            # Try with evil-winrm
            cmd = [
                "evil-winrm",
                "-i", target,
                "-u", user_string,
                "-p", password,
                "-e", command
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout * 2,
                text=True
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    def get_method_name(self) -> str:
        """Get authentication method name"""
        return self.method_name
