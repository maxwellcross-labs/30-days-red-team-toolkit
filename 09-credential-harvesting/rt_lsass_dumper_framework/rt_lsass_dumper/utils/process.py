#!/usr/bin/env python3
"""
Process management utilities for LSASS operations
"""

import subprocess
import psutil
from typing import Optional


def get_lsass_pid() -> Optional[int]:
    """
    Get LSASS process ID using multiple methods
    
    Returns:
        int: LSASS PID or None if not found
    """
    # Method 1: Try psutil (most reliable)
    try:
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'].lower() == 'lsass.exe':
                pid = proc.info['pid']
                print(f"[+] LSASS PID: {pid} (via psutil)")
                return pid
    except Exception:
        pass
    
    # Method 2: Try PowerShell
    try:
        ps_script = "(Get-Process lsass).Id"
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            pid = int(result.stdout.strip())
            print(f"[+] LSASS PID: {pid} (via PowerShell)")
            return pid
    except Exception:
        pass
    
    # Method 3: Try tasklist
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq lsass.exe', '/FO', 'CSV', '/NH'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            # Parse CSV output: "lsass.exe","PID","Services","0","Memory"
            parts = result.stdout.strip().split(',')
            if len(parts) >= 2:
                pid = int(parts[1].strip('"'))
                print(f"[+] LSASS PID: {pid} (via tasklist)")
                return pid
    except Exception:
        pass
    
    print(f"[-] Could not find LSASS process")
    return None


def verify_process_exists(pid: int) -> bool:
    """
    Verify that a process with given PID exists
    
    Args:
        pid: Process ID to verify
        
    Returns:
        bool: True if process exists
    """
    try:
        return psutil.pid_exists(pid)
    except Exception:
        return False


def get_process_info(pid: int) -> dict:
    """
    Get detailed information about a process
    
    Args:
        pid: Process ID
        
    Returns:
        dict: Process information
    """
    try:
        proc = psutil.Process(pid)
        
        return {
            'pid': pid,
            'name': proc.name(),
            'username': proc.username(),
            'status': proc.status(),
            'memory_mb': proc.memory_info().rss / 1024 / 1024,
            'num_threads': proc.num_threads()
        }
    
    except Exception as e:
        return {'error': str(e)}
