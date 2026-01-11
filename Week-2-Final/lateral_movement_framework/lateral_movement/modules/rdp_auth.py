#!/usr/bin/env python3
"""
RDP Authentication Module
Tests Remote Desktop Protocol authentication
"""

import subprocess
from typing import Tuple, Optional


class RDPAuthenticator:
    """
    RDP authentication testing
    Uses xfreerdp for credential validation
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize RDP authenticator
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
        self.method_name = "RDP"
        self.default_port = 3389
    
    def test_authentication(self, target: str, username: str, password: str, 
                          domain: str = None) -> Tuple[bool, str]:
        """
        Test RDP authentication against target
        
        Args:
            target: Target IP or hostname
            username: Username for authentication
            password: Password for authentication
            domain: Optional domain
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Build xfreerdp command for auth-only test
            cmd = [
                "xfreerdp",
                f"/v:{target}",
                f"/u:{username}",
                f"/p:{password}",
                "+auth-only",
                "/cert:ignore",
                "-clipboard",
                "/timeout:{}".format(self.timeout * 1000)  # xfreerdp uses milliseconds
            ]
            
            if domain:
                cmd.append(f"/d:{domain}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout + 5,  # Add buffer for process startup
                text=True
            )
            
            # Check output for authentication success indicators
            output = result.stdout + result.stderr
            
            if "Authentication only" in output or "authentication only" in output.lower():
                if "success" in output.lower() or result.returncode == 0:
                    return True, "RDP authentication successful"
                elif "denied" in output.lower() or "failed" in output.lower():
                    return False, "Invalid credentials"
            
            # Check for specific error conditions
            if "logon failure" in output.lower() or "wrong password" in output.lower():
                return False, "Invalid credentials"
            elif "connection refused" in output.lower() or "unable to connect" in output.lower():
                return False, "RDP port closed or filtered"
            elif "network" in output.lower() and "unreachable" in output.lower():
                return False, "Network unreachable"
            elif result.returncode == 0:
                # Command succeeded, likely authenticated
                return True, "RDP authentication successful"
            else:
                return False, "RDP authentication failed"
        
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except FileNotFoundError:
            return False, "xfreerdp not installed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_nla_required(self, target: str) -> Tuple[bool, str]:
        """
        Check if Network Level Authentication (NLA) is required
        
        Args:
            target: Target IP or hostname
            
        Returns:
            Tuple of (nla_required, message)
        """
        try:
            cmd = [
                "nmap",
                "-p", str(self.default_port),
                "--script", "rdp-enum-encryption",
                target
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if "CredSSP" in result.stdout or "NLA" in result.stdout:
                return True, "NLA is required"
            else:
                return False, "NLA is not required"
        
        except FileNotFoundError:
            return None, "nmap not installed"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def get_method_name(self) -> str:
        """Get authentication method name"""
        return self.method_name
