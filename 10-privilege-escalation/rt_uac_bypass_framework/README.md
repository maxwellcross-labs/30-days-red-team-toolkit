# UAC Bypass Framework

A modular Python framework for bypassing Windows User Account Control (UAC) using multiple techniques for different Windows versions.

## ⚠️ Legal Disclaimer

This tool is intended for authorized penetration testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## Overview

Windows UAC (User Account Control) prompts users for consent when applications attempt to perform administrative actions. This framework implements multiple UAC bypass techniques that allow executing payloads with elevated privileges without triggering the UAC prompt.

**Note**: UAC bypass requires administrator privileges. Use privilege escalation techniques first if needed.

## Features

- Multiple UAC bypass techniques
- Automatic Windows version detection
- Automatic method selection based on OS compatibility
- Registry-based and environment hijacking techniques
- OPSEC-conscious automatic cleanup
- Comprehensive testing and validation
- Detailed compatibility reports

## Directory Structure

```
uac_bypass_framework/
├── __init__.py              # Package initialization
├── uac_bypass.py            # Main CLI entry point
├── README.md                # This file
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── base.py              # Abstract base class for bypasses
│   ├── detector.py          # Windows version detection
│   └── uac_checker.py       # UAC status checking
│
├── bypasses/                # Individual bypass techniques
│   ├── __init__.py
│   ├── fodhelper.py         # Fodhelper.exe bypass
│   ├── eventvwr.py          # Event Viewer bypass
│   ├── sdclt.py             # Sdclt.exe bypass
│   ├── computerdefaults.py  # ComputerDefaults.exe bypass
│   ├── slui.py              # Slui.exe bypass
│   └── diskcleanup.py       # Disk Cleanup bypass
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── helpers.py           # Helper utilities
│   ├── selector.py          # Automatic method selection
│   └── reporter.py          # Report generation
│
└── output/                  # Logs and reports
```

## Installation

```bash
# Clone or copy the framework
git clone <repo> uac_bypass_framework
cd uac_bypass_framework

# No additional dependencies required (uses standard library)
```

## Quick Start

### Enumerate Compatible Methods

```bash
python uac_bypass.py --enumerate
```

### Automatic Bypass

```bash
python uac_bypass.py --method auto --payload payload.exe
```

### Use Specific Method

```bash
# Fodhelper bypass
python uac_bypass.py --method fodhelper --payload payload.exe

# Disk Cleanup bypass (most reliable)
python uac_bypass.py --method diskcleanup --payload payload.exe
```

### Test All Methods

```bash
python uac_bypass.py --test-all --payload test_payload.exe
```

### Generate Report

```bash
python uac_bypass.py --enumerate --report uac_report --report-format both
```

## Available Bypass Methods

| Method | Windows Version | Max Build | Success Rate | Detection Risk |
|--------|-----------------|-----------|--------------|----------------|
| fodhelper | Windows 10 | 17763 (1809) | 85% | Medium |
| eventvwr | Windows 7/8/10 | 14393 | 90% | Low |
| sdclt | Windows 10 | 17134 (1803) | 80% | Medium |
| computerdefaults | Windows 10 | 17134 (1803) | 75% | Low |
| slui | Windows 8/10 | 17763 (1809) | 70% | Medium |
| diskcleanup | Windows 7+ | 99999 | 85% | Low |

## Module Usage

### As a Library

```python
from rt_uac_bypass_framework import (
    SystemDetector,
    UACChecker,
    FodhelperBypass,
    DiskCleanupBypass
)
from rt_uac_bypass_framework.utils.selector import BypassSelector

# Check system
detector = SystemDetector()
checker = UACChecker()

print(f"Windows: {detector.get_version_name()}")
print(f"UAC Enabled: {checker.is_uac_enabled()}")

# Auto-select best method
selector = BypassSelector()
best_method = selector.select_best_method()

# Or use specific bypass
bypass = DiskCleanupBypass(verbose=True)
success = bypass.execute("C:\\payload.exe")
```

## How UAC Bypass Works

### Registry Hijacking (fodhelper, eventvwr, etc.)

1. Auto-elevating Windows binaries check HKCU registry for shell handlers
2. We create registry keys pointing to our payload
3. When the binary runs, it executes our payload with elevated privileges
4. Registry keys are cleaned up afterward

### Environment Variable Hijacking (diskcleanup)

1. The SilentCleanup scheduled task runs with elevated privileges
2. It references `%windir%` environment variable
3. We temporarily hijack the user's `windir` variable to include our payload
4. When the task runs, our payload executes elevated
5. Original environment variable is restored

## OPSEC Considerations

- **Automatic Cleanup**: All registry modifications are tracked and cleaned up
- **Timestamp Preservation**: Not applicable (registry-based)
- **Detection**: Some methods are more likely to trigger security software
- **Recommended**: Use `diskcleanup` method for lowest detection risk

## Prerequisites

- Windows operating system
- **Administrator privileges** (UAC bypass requires admin)
- Payload executable

## Defense Recommendations

1. **Configure UAC to Always Notify** - Set to highest level
2. **Use Credential Guard** - Prevents some bypass techniques
3. **Monitor Registry Changes** - Alert on HKCU\Software\Classes modifications
4. **Application Whitelisting** - Prevent unauthorized executables
5. **Keep Windows Updated** - Microsoft patches bypass techniques
6. **EDR Solutions** - Modern EDR can detect UAC bypass attempts

## References

- [MITRE ATT&CK - Bypass User Account Control](https://attack.mitre.org/techniques/T1548/002/)
- [UACME - UACMe GitHub](https://github.com/hfiref0x/UACME)
- [PayloadsAllTheThings - UAC Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)

## License

For educational and authorized testing purposes only.