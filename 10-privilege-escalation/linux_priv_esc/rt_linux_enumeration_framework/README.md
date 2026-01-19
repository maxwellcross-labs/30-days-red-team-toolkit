# RT Linux Privilege Escalation Framework

> **Part of the 30 Days of Red Team Toolkit**

A modular, professional-grade Linux privilege escalation enumeration framework designed for red team operators and penetration testers.

```
╔═══════════════════════════════════════════════════════════════╗
║     Linux Privilege Escalation Enumerator                     ║
║     "Find the path. Escalate. Own the box."                   ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🎯 Features

- **Modular Architecture**: Each enumeration vector is a separate, maintainable module
- **Comprehensive Coverage**: SUID, sudo, cron, capabilities, containers, NFS, and more
- **GTFOBins Integration**: Automatic cross-referencing with known exploitable binaries
- **Severity Classification**: Findings ranked by exploitability (Critical → Info)
- **Multiple Report Formats**: JSON, text, and exploitation guides
- **Extensible Design**: Easy to add new enumeration modules

## 📦 Installation

```bash
# Clone or copy the rt_linux_privesc directory
cd /path/to/toolkit

# Run directly
python3 -m rt_linux_privesc

# Or import in your scripts
from rt_linux_privesc import LinuxPrivEscEnumerator
```

## 🚀 Quick Start

### Command Line

```bash
# Full enumeration
python3 -m rt_linux_privesc

# Specify output directory
python3 -m rt_linux_privesc --output /tmp/scan_results

# Verbose mode
python3 -m rt_linux_privesc --verbose

# Run specific enumerators only
python3 -m rt_linux_privesc --only suid sudo cron

# List available enumerators
python3 -m rt_linux_privesc --list
```

### Python API

```python
from rt_linux_privesc import LinuxPrivEscEnumerator, Config

# Basic usage
enumerator = LinuxPrivEscEnumerator()
enumerator.run_all()
enumerator.generate_report()

# Custom configuration
config = Config(
    output_dir='/tmp/results',
    timeout=120,
    verbose=True
)
enumerator = LinuxPrivEscEnumerator(config=config)
enumerator.run_all()

# Access findings programmatically
for finding in enumerator.findings.get_critical():
    print(f"[CRITICAL] {finding.category}: {finding.target}")
    print(f"  Exploit: {finding.exploitation}")
```

## 📋 Enumeration Modules

| Module | Description | Severity Range |
|--------|-------------|----------------|
| **Privileges** | Current user context and group memberships | Critical - Info |
| **SUID** | SUID/SGID binaries with GTFOBins cross-reference | Critical - High |
| **Sudo** | Sudo permissions, NOPASSWD, version vulnerabilities | Critical - Low |
| **Cron** | Cron jobs, writable scripts, wildcard injection | Critical - Medium |
| **Writable** | Writable files in /etc, PATH, init scripts | Critical - Medium |
| **Capabilities** | Linux capabilities on binaries | Critical - High |
| **Containers** | Docker/LXD/Podman socket access | Critical - Info |
| **NFS** | NFS shares with no_root_squash | Critical - Medium |

## 📊 Output Files

After enumeration, three report files are generated:

```
/tmp/privesc_enum/
├── privesc_report.json      # Full structured report
├── privesc_report.txt       # Human-readable report
└── exploitation_guide.txt   # Quick exploitation reference
```

### JSON Report Structure

```json
{
  "metadata": {
    "tool": "Linux Privilege Escalation Enumerator",
    "hostname": "target-server",
    "user": "www-data",
    "start_time": "2024-01-15T10:30:00"
  },
  "summary": {
    "critical": 3,
    "high": 5,
    "medium": 2,
    "low": 1,
    "info": 4
  },
  "findings": {
    "critical": ["..."],
    "high": ["..."],
    "..."
  }
}
```

## 🔍 Enumeration Details

### SUID/SGID Binaries

Searches for binaries with SUID/SGID bits set and cross-references with:
- **GTFOBins**: Known exploitable binaries
- **Common System Binaries**: Standard binaries (filtered out)
- **Unusual Binaries**: Custom/third-party SUID binaries

### Sudo Permissions

Analyzes `sudo -l` output for:
- **NOPASSWD entries**: Highest priority - no password required
- **Wildcards**: Argument injection opportunities
- **GTFOBins commands**: Known exploitation paths
- **Version vulnerabilities**: CVE-2021-3156 (Baron Samedit)

### Cron Jobs

Examines cron for:
- **Writable scripts**: Direct code injection
- **Missing scripts**: Create script in writable directory
- **Wildcard injection**: tar, rsync checkpoint exploitation
- **PATH hijacking**: Writable directories in cron PATH

### Capabilities

Identifies dangerous Linux capabilities:
- `cap_setuid`: Change UID to root
- `cap_sys_admin`: Container escape, mount operations
- `cap_dac_override`: Bypass file permissions
- `cap_sys_ptrace`: Process injection

## ⚠️ Legal Disclaimer

This tool is intended for **authorized security testing only**.

- Always obtain proper authorization before testing
- Use responsibly in controlled environments
- The authors are not responsible for misuse

## 🏗️ Architecture

```
rt_linux_privesc/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── core/
│   ├── __init__.py
│   ├── base.py          # BaseEnumerator abstract class
│   ├── config.py        # Configuration management
│   ├── enumerator.py    # Main orchestrator
│   └── findings.py      # Finding data structures
├── enumerators/
│   ├── __init__.py
│   ├── privileges.py    # User/group enumeration
│   ├── suid.py          # SUID/SGID enumeration
│   ├── sudo.py          # Sudo enumeration
│   ├── cron.py          # Cron enumeration
│   ├── writable.py      # Writable files enumeration
│   ├── capabilities.py  # Capabilities enumeration
│   ├── containers.py    # Container enumeration
│   └── nfs.py           # NFS enumeration
└── utils/
    ├── __init__.py
    └── helpers.py       # Utility functions
```

## 🔧 Extending the Framework

Create a new enumerator by extending `BaseEnumerator`:

```python
from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity

class CustomEnumerator(BaseEnumerator):
    name = "Custom Enumerator"
    description = "Description of what this checks"
    
    def enumerate(self) -> None:
        self.print_header()
        
        # Your enumeration logic here
        result = self.run_command("your-command")
        
        if result:
            self.add_finding(
                category="Custom Category",
                severity=FindingSeverity.HIGH,
                finding="What was found",
                exploitation="How to exploit it",
                impact="Expected impact",
                target="/path/to/target"
            )
```

## 📚 Resources

- [GTFOBins](https://gtfobins.github.io/) - Unix binaries exploitation
- [HackTricks - Linux Privilege Escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md)

---

**30 Days of Red Team** | *From Zero Access to Domain Admin*