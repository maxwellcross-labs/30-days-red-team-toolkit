#!/usr/bin/env python3
"""
Access Verification Module
Confirms initial access is functional before proceeding
"""

import subprocess
from typing import Tuple, Optional


class AccessVerifier:
    """
    Verifies initial access to target system
    Tests shell connectivity and basic command execution
    """
    
    def __init__(self, target_ip: str, port: int = 4444):
        """
        Initialize access verifier
        
        Args:
            target_ip: Target system IP address
            port: Shell listener port
        """
        self.target_ip = target_ip
        self.port = port
    
    def test_shell_connectivity(self, timeout: int = 5) -> Tuple[bool, str]:
        """
        Test basic shell connectivity
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Test basic command execution
            result = subprocess.run(
                ["nc", self.target_ip, str(self.port)],
                input=b"whoami\n",
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, "Shell connectivity confirmed"
            else:
                return False, f"No response from shell (return code: {result.returncode})"
                
        except subprocess.TimeoutExpired:
            return False, f"Connection timeout after {timeout} seconds"
        except FileNotFoundError:
            return False, "netcat (nc) not found - install netcat to test connectivity"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_command_execution(self, command: str = "whoami", timeout: int = 5) -> Tuple[bool, str]:
        """
        Test command execution capability
        
        Args:
            command: Test command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, output/error)
        """
        try:
            result = subprocess.run(
                ["nc", self.target_ip, str(self.port)],
                input=f"{command}\n".encode(),
                capture_output=True,
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout:
                output = result.stdout.decode('utf-8', errors='ignore').strip()
                return True, f"Command executed: {output[:100]}"
            else:
                return False, "No output from command"
                
        except subprocess.TimeoutExpired:
            return False, f"Command timeout after {timeout} seconds"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    def verify_access(self) -> Tuple[bool, str]:
        """
        Complete access verification
        
        Returns:
            Tuple of (success, detailed_message)
        """
        # Test 1: Basic connectivity
        connected, conn_msg = self.test_shell_connectivity()
        if not connected:
            return False, f"Connectivity failed: {conn_msg}"
        
        # Test 2: Command execution
        executed, exec_msg = self.test_command_execution()
        if not executed:
            return False, f"Command execution failed: {exec_msg}"
        
        return True, "Initial access verified - shell is functional"
