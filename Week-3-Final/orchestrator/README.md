# Week 3 Attack Orchestrator

A modular Python framework for chaining red team techniques during authorized security assessments.

## Overview

This orchestrator integrates the following attack phases:

1. **Privilege Escalation** - Escalate from user to Admin/SYSTEM (Windows) or root (Linux)
2. **Credential Harvesting** - Extract credentials from LSASS, SAM, registry, DPAPI, etc.
3. **Lateral Movement** - Move across the network using Pass-the-Hash, WMI, PSRemoting
4. **Network Pivoting** - Access isolated networks through SSH tunnels, Chisel, etc.
5. **Trust Exploitation** - Exploit AD trust relationships for cross-domain access

## Project Structure

```
Week-3-Final/
├── orchestrator/
│   ├── __init__.py               # Package initialization
│   ├── __main__.py               # Module entry point
│   ├── cli.py                    # Command-line interface
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── enums.py              # Platform, PrivilegeLevel enums
│   │   ├── credential.py         # Credential dataclass
│   │   ├── system.py             # CompromisedSystem dataclass
│   │   └── state.py              # AttackState dataclass
│   ├── phases/                   # Attack phases
│   │   ├── __init__.py
│   │   ├── base.py               # Base phase class
│   │   ├── privesc.py            # Phase 1: Privilege Escalation
│   │   ├── credential_harvest.py # Phase 2: Credential Harvesting
│   │   ├── lateral_movement.py   # Phase 3: Lateral Movement
│   │   ├── pivoting.py           # Phase 4: Network Pivoting
│   │   └── trust_exploit.py      # Phase 5: Trust Exploitation
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Main orchestrator
│   │   ├── logger.py             # Operation logging
│   │   └── reporter.py           # Report generation
│   └── README.md

```

## Installation

```bash
# Clone or copy the package
cd week3_orchestrator

# No external dependencies required for core functionality
# Optional: Install impacket for actual exploitation
pip install impacket
```

## Usage

### Command Line

```bash
# Run full attack chain on Windows target
python -m week3_orchestrator --platform windows

# Run specific phase only
python -m week3_orchestrator --phase 2 --platform windows

# Specify output directory and targets
python -m week3_orchestrator --output my_op --targets 192.168.1.0/24 10.0.0.0/24

# Show help
python -m week3_orchestrator --help
```

### Python API

```python
from week3_orchestrator import Week3Orchestrator, Platform

# Initialize
orchestrator = Week3Orchestrator(output_dir="my_operation")

# Run full chain
orchestrator.execute_full_chain(Platform.WINDOWS)

# Or run individual phases
orchestrator.phase1_privilege_escalation(Platform.WINDOWS)
credentials = orchestrator.phase2_credential_harvesting()
orchestrator.phase3_lateral_movement(credentials, ["192.168.1.0/24"])
orchestrator.phase4_network_pivoting()
orchestrator.phase5_domain_trust_exploitation()

# Generate reports
orchestrator.generate_reports()
```

### Working with Models

```python
from week3_orchestrator import (
    Credential,
    CompromisedSystem,
    Platform,
    PrivilegeLevel,
)

# Create a credential
cred = Credential(
    username="admin",
    domain="CORP",
    ntlm_hash="aad3b435b51404eeaad3b435b51404ee",
    source="LSASS dump",
)

# Create a compromised system
system = CompromisedSystem(
    hostname="WS01",
    ip_address="192.168.1.10",
    platform=Platform.WINDOWS,
    privilege_level=PrivilegeLevel.ADMIN,
)

# Add credentials to system
system.add_credential(cred)
```

## Output Files

The orchestrator generates:

- `operation.log` - Detailed operation log
- `operation.json` - Structured JSON log
- `operation_report.md` - Comprehensive Markdown report
- `operation_state.json` - Serialized attack state
- `executive_summary.md` - Brief executive summary

## Extending

### Adding New Phases

1. Create a new file in `phases/`
2. Inherit from `BasePhase`
3. Implement the `execute()` method
4. Register in `phases/__init__.py`

```python
from .base import BasePhase

class MyNewPhase(BasePhase):
    PHASE_NUMBER = 6
    PHASE_NAME = "MY NEW PHASE"
    
    def execute(self, **kwargs) -> bool:
        self.log_header()
        # Your phase logic here
        return True
```

### Custom Logging

```python
from week3_orchestrator.core import OperationLogger

logger = OperationLogger(output_dir="my_logs")
logger.info("Starting operation")
logger.success("Phase complete")
logger.warning("Potential issue")
logger.error("Something failed")
```

## Legal Disclaimer

**This tool is for authorized security testing only.**

Unauthorized access to computer systems is illegal. Always obtain written permission before conducting security assessments. The techniques demonstrated should only be used in authorized penetration tests with explicit scope.

## Author

Created as part of the "30 Days of Red Team" series.