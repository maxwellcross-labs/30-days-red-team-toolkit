#!/usr/bin/env python3
"""
SMB Authentication Module
Tests SMB/CIFS authentication against targets
"""

import subprocess
from typing import Tuple, Optional


class SMBAuthenticator:
    """
    SMB/CIFS authentication testing
    Uses smbclient for credential validation
    """
    
    def __init__(self, timeout: int = 5):
        """
        Initialize SMB authenticator
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
        self.method_name = "SMB"
    
    def test_authentication(self, target: str, username: str, password: str, domain: str = None) -> Tuple[bool, str]:
        """
        Test SMB authentication against target
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            domain: Optional domain
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Build username with domain if provided
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            # Test SMB connection to C$ admin share
            cmd = [
                "smbclient",
                f"//{target}/C$",
                "-U", f"{user_string}%{password}",
                "-c", "ls"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode == 0:
                return True, "SMB authentication successful"
            
            # Check for specific error messages
            stderr = result.stderr.lower()
            
            if "logon failure" in stderr or "access denied" in stderr:
                return False, "Invalid credentials"
            elif "connection refused" in stderr:
                return False, "SMB port closed or filtered"
            elif "timed out" in stderr or "timeout" in stderr:
                return False, "Connection timeout"
            else:
                return False, f"SMB authentication failed: {result.stderr[:100]}"
        
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except FileNotFoundError:
            return False, "smbclient not installed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_shares(self, target: str, username: str, password: str, domain: str = None) -> Tuple[bool, list]:
        """
        Enumerate accessible shares
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            domain: Optional domain
            
        Returns:
            Tuple of (success, list of shares)
        """
        try:
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            cmd = [
                "smbclient",
                "-L", target,
                "-U", f"{user_string}%{password}",
                "-N"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode == 0:
                # Parse shares from output
                shares = []
                for line in result.stdout.split('\n'):
                    if 'Disk' in line or 'IPC' in line:
                        parts = line.split()
                        if parts:
                            shares.append(parts[0])
                
                return True, shares
            
            return False, []
        
        except Exception as e:
            return False, []
    
    def upload_file(self, target: str, username: str, password: str, 
                    local_file: str, remote_path: str, domain: str = None) -> Tuple[bool, str]:
        """
        Upload file via SMB
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            local_file: Local file path
            remote_path: Remote destination path
            domain: Optional domain
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            cmd = [
                "smbclient",
                f"//{target}/C$",
                "-U", f"{user_string}%{password}",
                "-c", f"put {local_file} {remote_path}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout * 2,  # Upload may take longer
                text=True
            )
            
            if result.returncode == 0:
                return True, f"File uploaded to {remote_path}"
            else:
                return False, f"Upload failed: {result.stderr[:100]}"
        
        except Exception as e:
            return False, f"Upload error: {str(e)}"
    
    def get_method_name(self) -> str:
        """Get authentication method name"""
        return self.method_name
