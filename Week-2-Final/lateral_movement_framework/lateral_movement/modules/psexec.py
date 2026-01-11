#!/usr/bin/env python3
"""
PsExec Module
Remote execution using Impacket psexec
"""

import subprocess
from typing import Tuple, Optional


class PsExecAuthenticator:
    """
    PsExec-style remote execution
    Uses Impacket's psexec.py for credential validation and execution
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize PsExec authenticator
        
        Args:
            timeout: Execution timeout in seconds
        """
        self.timeout = timeout
        self.method_name = "PsExec"
    
    def test_authentication(self, target: str, username: str, password: str,
                          domain: str = None) -> Tuple[bool, str]:
        """
        Test PsExec authentication against target
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            domain: Optional domain
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Build credential string
            if domain:
                cred_string = f"{domain}/{username}:{password}"
            else:
                cred_string = f"{username}:{password}"
            
            # Test with simple whoami command
            cmd = [
                "psexec.py",
                f"{cred_string}@{target}",
                "whoami"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode == 0:
                # Successfully executed command
                return True, "PsExec authentication successful"
            
            # Check for authentication errors
            stderr = result.stderr.lower()
            
            if "logon failure" in stderr or "access is denied" in stderr:
                return False, "Invalid credentials"
            elif "connection refused" in stderr or "unreachable" in stderr:
                return False, "Target unreachable or SMB port closed"
            elif "timed out" in stderr:
                return False, "Connection timeout"
            else:
                return False, f"PsExec failed: {result.stderr[:100]}"
        
        except subprocess.TimeoutExpired:
            return False, "Execution timeout"
        except FileNotFoundError:
            return False, "psexec.py not installed (Impacket required)"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def execute_command(self, target: str, username: str, password: str,
                       command: str, domain: str = None) -> Tuple[bool, str]:
        """
        Execute command via PsExec
        
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
                cred_string = f"{domain}/{username}:{password}"
            else:
                cred_string = f"{username}:{password}"
            
            cmd = [
                "psexec.py",
                f"{cred_string}@{target}",
                command
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
        
        except subprocess.TimeoutExpired:
            return False, "Execution timeout"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    def upload_and_execute(self, target: str, username: str, password: str,
                          local_file: str, remote_path: str = None, 
                          domain: str = None) -> Tuple[bool, str]:
        """
        Upload file and execute via PsExec
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            local_file: Local file to upload
            remote_path: Remote path (default: C:\\Windows\\Temp\\<filename>)
            domain: Optional domain
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import os
            
            if domain:
                cred_string = f"{domain}/{username}:{password}"
            else:
                cred_string = f"{username}:{password}"
            
            # Default remote path
            if remote_path is None:
                filename = os.path.basename(local_file)
                remote_path = f"C:\\Windows\\Temp\\{filename}"
            
            # First, upload using smbclient
            upload_cmd = [
                "smbclient",
                f"//{target}/C$",
                "-U", f"{username}%{password}",
                "-c", f"put {local_file} {remote_path.replace('C:', '')}"
            ]
            
            upload_result = subprocess.run(
                upload_cmd,
                capture_output=True,
                timeout=self.timeout * 2,
                text=True
            )
            
            if upload_result.returncode != 0:
                return False, f"Upload failed: {upload_result.stderr[:100]}"
            
            # Then execute using psexec
            exec_cmd = [
                "psexec.py",
                f"{cred_string}@{target}",
                remote_path
            ]
            
            exec_result = subprocess.run(
                exec_cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if exec_result.returncode == 0:
                return True, f"File uploaded and executed: {remote_path}"
            else:
                return False, f"Execution failed: {exec_result.stderr[:100]}"
        
        except subprocess.TimeoutExpired:
            return False, "Operation timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_method_name(self) -> str:
        """Get authentication method name"""
        return self.method_name
