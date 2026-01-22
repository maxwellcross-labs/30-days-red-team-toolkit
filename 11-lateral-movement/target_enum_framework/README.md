# Target Enumeration Framework

A professional, modular Python framework for discovering lateral movement targets during authorized penetration testing and red team operations.

> ⚠️ **LEGAL DISCLAIMER**: This tool is intended for authorized security testing only. Unauthorized scanning of computer networks is illegal. Always obtain written permission before testing.

## Features

- **Multi-Protocol Scanning**: SMB, WinRM, RDP, SSH
- **Automatic Categorization**: Windows, Linux, Domain Controllers
- **High-Value Target Identification**: DCs, File Servers, Databases, Mail Servers
- **Target List Generation**: Ready-to-use files for other tools
- **Comprehensive Reporting**: JSON reports with full details
- **Modular Architecture**: Easy to extend with new scanners

## Installation

```bash
# Clone the repository
git clone https://github.com/maxwellcross/target-enum-framework.git
cd target-enum-framework

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- CrackMapExec (for SMB/WinRM scanning)
- nmap (for RDP/SSH scanning)

## Quick Start

### Command Line

```bash
# Full auto enumeration (all protocols)
python -m target_enum_framework --network 192.168.1.0/24

# Windows-focused (SMB, WinRM, RDP)
python -m target_enum_framework --network 192.168.1.0/24 --protocols smb winrm rdp

# Linux-focused (SSH only)
python -m target_enum_framework --network 192.168.1.0/24 --protocol ssh

# Quick SMB scan
python -m target_enum_framework --network 192.168.1.0/24 --protocol smb

# List available protocols
python -m target_enum_framework --list-protocols
```

### Python API

```python
from target_enum_framework import TargetEnumerationFramework

# Initialize framework
framework = TargetEnumerationFramework()

# Full auto enumeration
collection = framework.auto_enumerate("192.168.1.0/24")

# Get target lists
windows_targets = framework.get_targets('windows')
linux_targets = framework.get_targets('linux')
high_value = framework.get_targets('high_value')
domain_controllers = framework.get_targets('domain_controllers')

# Or scan specific protocols
collection = framework.scan_protocols(
    "192.168.1.0/24",
    protocols=["smb", "winrm"]
)

# Manually identify high-value targets
framework.identify_high_value()

# Generate reports
framework.generate_reports()
```

## Supported Protocols

### SMB (Port 445)

Primary Windows lateral movement protocol. Uses CrackMapExec.

```bash
python -m target_enum_framework -n 192.168.1.0/24 -p smb
```

**Identifies:**
- Windows hosts
- Domain Controllers
- Samba servers

### WinRM (Port 5985/5986)

PowerShell Remoting targets. Uses CrackMapExec.

```bash
python -m target_enum_framework -n 192.168.1.0/24 -p winrm
```

**Targets for:**
- evil-winrm
- Enter-PSSession
- Invoke-Command

### RDP (Port 3389)

Remote Desktop targets. Uses nmap.

```bash
python -m target_enum_framework -n 192.168.1.0/24 -p rdp
```

**Targets for:**
- Standard RDP
- Pass-the-Hash RDP (Restricted Admin)
- xfreerdp

### SSH (Port 22)

Linux lateral movement targets. Uses nmap.

```bash
python -m target_enum_framework -n 192.168.1.0/24 -p ssh
```

**Targets for:**
- Key-based auth
- Password auth
- SSH tunneling/pivoting

## High-Value Target Detection

The framework automatically identifies high-value targets based on hostname patterns:

| Category | Keywords |
|----------|----------|
| Domain Controller | DC, DOMAIN, CONTROLLER, AD, PDC |
| File Server | FILE, FS, SHARE, NAS |
| Database | SQL, DATABASE, DB, ORACLE, MYSQL |
| Mail Server | EXCHANGE, MAIL, SMTP |
| Backup Server | BACKUP, BKP |
| Sensitive | VAULT, SECRET, ADMIN, MGMT |

## Output Files

All output is saved to the specified directory (default: `lm_targets/`):

| File | Description |
|------|-------------|
| `windows_targets.txt` | All Windows hosts (one IP per line) |
| `linux_targets.txt` | All Linux hosts |
| `high_value_targets.txt` | High-value targets |
| `domain_controllers.txt` | Identified DCs |
| `all_targets.txt` | All discovered hosts |
| `targets_report.json` | Comprehensive JSON report |

### JSON Report Structure

```json
{
    "timestamp": "2025-01-20T12:00:00",
    "network": "192.168.1.0/24",
    "summary": {
        "total_hosts": 50,
        "windows_hosts": 35,
        "linux_hosts": 15,
        "domain_controllers": 2,
        "high_value_targets": 8
    },
    "targets": {
        "windows_hosts": [...],
        "linux_hosts": [...],
        "domain_controllers": [...],
        "high_value": [...],
        "all_hosts": [...]
    }
}
```

## Project Structure

```
target_enum_framework/
├── __init__.py          # Package exports and version
├── __main__.py          # CLI entry point
├── core/
│   ├── __init__.py
│   ├── models.py        # Dataclasses and enums
│   ├── analyzer.py      # High-value target analyzer
│   └── framework.py     # Main orchestrator
├── scanners/
│   ├── __init__.py      # Scanner factory
│   ├── base.py          # Abstract base scanner
│   ├── smb.py           # CrackMapExec SMB
│   ├── winrm.py         # CrackMapExec WinRM
│   ├── rdp.py           # nmap RDP
│   └── ssh.py           # nmap SSH
├── reports/
│   ├── __init__.py
│   └── generator.py     # Report generation
└── utils/
    ├── __init__.py
    ├── output.py        # Console output handling
    ├── executor.py      # Command execution
    ├── network.py       # IP/network utilities
    └── files.py         # File operations
```

## Extending the Framework

### Adding New Scanner

1. Create new file in `scanners/`:

```python
from .base import BaseScanner
from ..core.models import Protocol, HostInfo, OperatingSystem

class NewScanner(BaseScanner):
    protocol = Protocol.NEW_PROTO
    default_port = 1234
    
    def build_command(self, network):
        return f"newtool scan {network}"
    
    def parse_output(self, output_text):
        hosts = []
        # Parse logic here
        return hosts
```

2. Register in `scanners/__init__.py`:

```python
SCANNER_REGISTRY['newproto'] = NewScanner
```

### Adding High-Value Keywords

Edit `core/models.py`:

```python
HIGH_VALUE_KEYWORDS = [
    # ... existing keywords ...
    ('NEWKEYWORD', TargetCategory.HIGH_VALUE),
]
```

## OPSEC Considerations

| Protocol | Tool | Noise Level |
|----------|------|-------------|
| SMB | CrackMapExec | Medium |
| WinRM | CrackMapExec | Medium |
| RDP | nmap | Low |
| SSH | nmap | Low |

**Tips:**
- Use targeted scans vs. broad sweeps when possible
- Consider timing/rate limiting in sensitive environments
- SMB enumeration may trigger security alerts
- Results can feed directly into lateral movement tools

## Author

**Maxwell Cross** - Red Team Operator & Security Researcher

## License

For authorized security testing only. See LICENSE for details.