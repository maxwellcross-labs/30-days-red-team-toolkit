# SSH Tunneling Framework v2.0

**Professional SSH port forwarding and SOCKS proxy management for penetration testing and red team operations.**

## 🎯 Overview

The SSH Tunneling Framework is a complete, production-ready toolkit for managing SSH tunnels during security assessments. Built with a modular architecture, it provides multiple tunneling methods with comprehensive error handling, validation, and operational features.

## ✨ Features

### Core Capabilities
- **Local Port Forwarding** (`-L`): Access internal services through compromised hosts
- **Remote Port Forwarding** (`-R`): Expose attacker services to pivot hosts
- **Dynamic Port Forwarding** (`-D`): SOCKS proxy for full network pivoting
- **Jump Host Tunneling** (`-J`): Multi-hop SSH connections

### Professional Features
- 🔒 Input validation and security checks
- 📊 Active tunnel management and tracking
- ⚙️ Automatic proxychains configuration
- 🔍 Process monitoring and cleanup
- 📝 Comprehensive logging
- 🎨 Clean CLI interface with helpful examples

## 📦 Installation

### From Source
```bash
git clone <repository>
cd ssh_tunneling_framework
pip install -e .
```

### Dependencies
- Python 3.7+
- SSH client (OpenSSH)
- Standard Python libraries only (no external dependencies)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed examples.

### Local Port Forward
Access internal RDP server through compromised DMZ host:
```bash
python -m ssh_tunneling.cli.main \
  --type local \
  --pivot-host 10.0.0.1 \
  --pivot-user root \
  --pivot-key ~/.ssh/id_rsa \
  --target-host 192.168.1.100 \
  --target-port 3389 \
  --local-port 3389
```

Then connect: `xfreerdp /v:localhost:3389`

### SOCKS Proxy
Create dynamic tunnel for network scanning:
```bash
python -m ssh_tunneling.cli.main \
  --type dynamic \
  --pivot-host 10.0.0.1 \
  --pivot-user root \
  --pivot-key ~/.ssh/id_rsa \
  --socks-port 1080
```

Then use: `proxychains4 -f ssh_tunnels/proxychains.conf nmap -sT 192.168.1.0/24`

### Remote Port Forward
Expose attacker web server on pivot:
```bash
python -m ssh_tunneling.cli.main \
  --type remote \
  --pivot-host 10.0.0.1 \
  --pivot-user root \
  --pivot-key ~/.ssh/id_rsa \
  --target-port 8080 \
  --remote-port 80
```

## 📚 Project Structure

```
ssh_tunneling_framework/
├── ssh_tunneling/
│   ├── core/
│   │   ├── base_tunnel.py      # Abstract base class for tunnels
│   │   └── tunnel_manager.py   # Tunnel management and tracking
│   ├── tunnels/
│   │   ├── local_forward.py    # Local port forwarding
│   │   ├── remote_forward.py   # Remote port forwarding
│   │   ├── dynamic_forward.py  # SOCKS proxy
│   │   └── jump_host.py        # Jump host tunneling
│   ├── utils/
│   │   ├── config_generator.py # Config file generation
│   │   ├── process_manager.py  # Process management
│   │   └── validators.py       # Input validation
│   └── cli/
│       └── main.py             # CLI interface
├── examples/
│   └── example_usage.py        # Usage examples
├── README.md
├── QUICKSTART.md
└── requirements.txt
```

## 🔧 Management Commands

### List Active Tunnels
```bash
python -m ssh_tunneling.cli.main --list
```

### List All SSH Tunnel Processes
```bash
python -m ssh_tunneling.cli.main --list-processes
```

### Kill All Tunnels
```bash
python -m ssh_tunneling.cli.main --kill-all
```

## 🎓 Usage as a Library

```python
from ssh_tunneling import TunnelManager, LocalForwardTunnel

# Initialize manager
manager = TunnelManager(output_dir="tunnels")

# Create local port forward
tunnel = LocalForwardTunnel(
    pivot_host="10.0.0.1",
    pivot_user="root",
    pivot_key="/home/user/.ssh/id_rsa",
    target_host="192.168.1.100",
    target_port=3389,
    local_port=3389
)

# Establish tunnel
if manager.add_tunnel(tunnel):
    print("[+] Tunnel established!")
    manager.list_active_tunnels()
```

## 🛡️ Operational Security

### Best Practices
1. **Key Management**: Use dedicated SSH keys for operations
2. **Port Selection**: Use non-standard ports when possible
3. **Cleanup**: Always kill tunnels after operations
4. **Logging**: Review logs for operational awareness
5. **Validation**: Framework validates all inputs before execution

### Detection Considerations
- SSH tunnels create persistent SSH connections
- Local port bindings are visible in network logs
- SOCKS proxy traffic may trigger IDS/IPS rules
- Consider using native SSH vs. this framework for stealth operations

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide with examples
- **[API Documentation](docs/API.md)**: Detailed API reference
- **Code Comments**: Comprehensive inline documentation

## 🤝 Contributing

Contributions welcome! This framework is designed for:
- Penetration testers
- Red team operators
- Security researchers
- Network administrators

## ⚖️ Legal Disclaimer

**FOR AUTHORIZED TESTING ONLY**

This framework is designed for legitimate security testing and network administration. Users must:
- Have explicit written authorization
- Comply with all applicable laws
- Use only on systems they own or have permission to test

Unauthorized access to computer systems is illegal. The authors assume no liability for misuse.

## 📜 License

MIT License - See LICENSE file for details

## 👤 Author

**Maxwell Cross**
- Red Team Operations
- Advanced Penetration Testing
- Security Tool Development

## 🔗 Related Projects

- **30 Days of Red Team**: Educational series on red team operations
- **Medium**: Technical articles on offensive security

---

**Remember**: Great power, great responsibility. Use this framework ethically and legally.
