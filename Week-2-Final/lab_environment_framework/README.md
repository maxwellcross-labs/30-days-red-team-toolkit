# Lab Environment Framework

**Professional-Grade Automated Red Team Lab Deployment**

Comprehensive framework for deploying complete red team practice environments with automated VM provisioning, monitoring, and C2 infrastructure.

## Overview

The Lab Environment Framework provides:

1. **Virtual Machine Deployment** - Automated Vagrant/VirtualBox setup
2. **Network Configuration** - Isolated lab network (192.168.100.0/24)
3. **Monitoring Stack** - Splunk, Zeek, Suricata
4. **C2 Infrastructure** - HTTPS and DNS C2 servers
5. **Vulnerable Scenarios** - Pre-configured attack targets

## Features

- ✅ **5 Virtual Machines** - DC, Web, File, Client, Linux
- ✅ **Blue Team Monitoring** - Complete detection stack
- ✅ **C2 Infrastructure** - Multi-channel command and control
- ✅ **Automated Setup** - One-command deployment
- ✅ **Verification** - Automated health checks
- ✅ **Modular Design** - Easy customization

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/lab-environment-framework.git
cd lab-environment-framework

# Deploy lab
python3 deploy_lab.py
```

Or programmatically:

```python
from lab_environment import LabDeployer

deployer = LabDeployer(lab_name="red-team-lab")
deployer.deploy_lab()
```

## Lab Components

### Virtual Machines

| VM | IP | Role | Resources |
|----|----|------|-----------|
| DC01 | 192.168.100.20 | Domain Controller | 2GB RAM, 2 CPU |
| WEB01 | 192.168.100.30 | Web Server | 2GB RAM, 2 CPU |
| FILE01 | 192.168.100.40 | File Server | 2GB RAM, 2 CPU |
| CLIENT01 | 192.168.100.50 | Windows 10 Client | 4GB RAM, 2 CPU |
| LINUX01 | 192.168.100.60 | Ubuntu Server | 2GB RAM, 2 CPU |

### Monitoring Stack

- **Splunk** - SIEM and log analysis (port 8000)
- **Zeek** - Network traffic analysis
- **Suricata** - IDS/IPS capabilities

### C2 Infrastructure

- **HTTPS C2** - Encrypted command channel (port 443)
- **DNS C2** - Covert DNS tunneling (c2.lab.local)

## Prerequisites

- VirtualBox 6.1+
- Vagrant 2.2+
- Docker & Docker Compose
- Ansible 2.9+
- Python 3.8+
- 20GB+ disk space
- 16GB+ RAM recommended

## Architecture

```
lab_environment_framework/
├── src/lab_environment/
│   ├── core/              # Configuration management
│   ├── modules/           # Component modules
│   └── deployers/         # Deployment orchestration
├── configs/               # Configuration files
├── scripts/               # Provisioning scripts
└── deploy_lab.py         # Main deployment script
```

## Usage Examples

### Deploy Complete Lab

```python
deployer = LabDeployer()
deployer.deploy_lab()
```

### Custom Configuration

```python
deployer = LabDeployer(lab_name="custom-lab")
deployer.network_subnet = "10.0.0.0/24"
deployer.deploy_lab()
```

### Verify Deployment

```python
deployer.verify_lab()
```

## Access Information

After deployment:

- **Splunk**: http://localhost:8000 (admin/Changeme123!)
- **Domain Controller**: 192.168.100.20
- **Web Server**: 192.168.100.30
- **File Server**: 192.168.100.40
- **Windows Client**: 192.168.100.50
- **Linux Server**: 192.168.100.60

## Customization

Edit configuration files in `configs/` directory:
- `vms.yaml` - VM definitions
- `network.yaml` - Network settings
- `monitoring.yaml` - Monitoring stack
- `c2.yaml` - C2 configuration

## Troubleshooting

**VMs not starting:**
- Check VirtualBox installation
- Verify virtualization enabled in BIOS
- Ensure sufficient RAM available

**Network connectivity issues:**
- Verify host-only network created
- Check firewall rules
- Ensure IP addresses don't conflict

**Monitoring not accessible:**
- Verify Docker running
- Check port availability
- Review Docker logs

## Legal & Ethical Use

⚠️ **AUTHORIZED USE ONLY** ⚠️

This lab environment is for:
- Security training and education
- Authorized penetration testing practice
- Red team skill development
- Defensive security training

Never deploy on production networks without authorization.

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## License

MIT License - See LICENSE file for details.

---

**Built by operators, for operators.** 🔴
