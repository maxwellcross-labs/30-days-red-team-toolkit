# Registry Credential Miner Framework

**Windows Registry Credential Extraction Toolkit**  
Part of the *30 Days of Red Team* Series

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED SECURITY TESTING ONLY**

This tool is designed for authorized penetration testing and security research. Unauthorized access to computer systems is illegal. Users are responsible for complying with applicable laws and obtaining proper authorization before use.

---

## 🎯 Overview

A professional-grade registry credential mining framework that extracts credentials from multiple Windows registry locations. Automates the discovery of plaintext passwords, encrypted credentials, and session information stored in the registry.

### Key Features

- **7 Credential Miners**: AutoLogon, RDP, WiFi, PuTTY, VNC, WinSCP, LSA Secrets
- **Multiple Privilege Levels**: User-level and admin miners
- **Professional Architecture**: Modular, extensible, production-ready
- **CLI & Library**: Use as command-line tool or Python library
- **Multiple Output Formats**: Text and JSON reports

---

## 📋 Requirements

- **OS**: Windows 10/11, Windows Server 2016+
- **Privileges**: Varies by miner (some require admin)
- **Python**: 3.8+
- **Optional**: Impacket (for LSA Secrets)

---

## 🚀 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/registry_miner_framework.git
cd registry_miner_framework

# Install optional dependencies
pip install -r requirements.txt

# Make executable
chmod +x registry_mine.py
```

### Package Install

```bash
# Install as package
pip install -e .

# Verify installation
python -c "import rt_registry_miner; print(registry_miner.__version__)"
```

---

## 💻 Usage

### Command-Line Interface

#### Basic Usage

```bash
# Check privileges and environment
python registry_mine.py check

# Mine all credential sources
python registry_mine.py mine --all

# Mine specific source
python registry_mine.py mine --target wifi
python registry_mine.py mine --target autologon
```

#### List Available Miners

```bash
# List all miners
python registry_mine.py list

# Show detailed miner info
python registry_mine.py info --miner putty
```

### Python Library Usage

#### Basic Mining

```python
from rt_registry_miner import RegistryCredentialMiner

# Initialize framework
miner = RegistryCredentialMiner(output_dir="output")

# Mine specific source
wifi_creds = miner.mine_target('wifi')

# Display results
for cred in wifi_creds:
    print(f"SSID: {cred['ssid']}, Password: {cred['password']}")
```

#### Comprehensive Mining

```python
from rt_registry_miner import RegistryCredentialMiner

miner = RegistryCredentialMiner()

# Mine all sources
findings = miner.mine_all()

# Generate report
miner.generate_report(save_json=True)

# Access specific findings
if findings['autologon']:
    for cred in findings['autologon']:
        print(f"User: {cred['username']}, Pass: {cred['password']}")
```

---

## 🎭 Credential Miners

### 1. AutoLogon (Requires: Admin)

**Extracts Windows AutoLogon credentials**

- **Location**: `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
- **Credentials**: Username, domain, plaintext password
- **Privilege**: Admin required

```bash
python registry_mine.py mine --target autologon
```

### 2. RDP Saved Connections (Requires: User)

**Extracts RDP connection information**

- **Location**: `HKCU\Software\Microsoft\Terminal Server Client\Servers`
- **Credentials**: Server addresses, username hints
- **Privilege**: Current user

```bash
python registry_mine.py mine --target rdp
```

### 3. WiFi Passwords (Requires: User/Admin)

**Extracts saved WiFi passwords**

- **Method**: `netsh wlan show profiles`
- **Credentials**: SSID names, plaintext passwords
- **Privilege**: User (own profiles), Admin (all profiles)

```bash
python registry_mine.py mine --target wifi
```

### 4. PuTTY Sessions (Requires: User)

**Extracts PuTTY session information**

- **Location**: `HKCU\Software\SimonTatham\PuTTY\Sessions`
- **Credentials**: Hostnames, usernames, proxy passwords (encrypted)
- **Privilege**: Current user

```bash
python registry_mine.py mine --target putty
```

### 5. VNC Passwords (Requires: Admin)

**Extracts VNC server passwords**

- **Locations**: Multiple VNC software paths
- **Credentials**: Encrypted passwords (weak encryption)
- **Privilege**: Admin required

```bash
python registry_mine.py mine --target vnc
```

### 6. WinSCP Sessions (Requires: User)

**Extracts WinSCP session information**

- **Location**: `HKCU\Software\Martin Prikryl\WinSCP 2\Sessions`
- **Credentials**: Hostnames, usernames, passwords (encrypted)
- **Privilege**: Current user

```bash
python registry_mine.py mine --target winscp
```

### 7. LSA Secrets (Requires: SYSTEM)

**Extracts LSA Secrets**

- **Location**: `HKLM\SECURITY`
- **Credentials**: DPAPI keys, service passwords, cached credentials
- **Privilege**: SYSTEM required
- **Tool**: Impacket secretsdump

```bash
python registry_mine.py mine --target lsa_secrets
```

---

## 📊 Output Files

The framework generates comprehensive reports:

```
registry_creds/
├── credential_report.txt       # Human-readable report
├── credential_report.json      # Machine-readable JSON
└── lsa_secrets.txt            # LSA secrets output (if mined)
```

### Report Formats

**Text Format**:
```
AUTOLOGON:
source: AutoLogon
username: administrator
domain: WORKGROUP
password: P@ssw0rd123

WIFI:
source: WiFi
ssid: HomeNetwork
password: wifipass123
```

**JSON Format**:
```json
{
  "autologon": [
    {
      "source": "AutoLogon",
      "username": "administrator",
      "password": "P@ssw0rd123"
    }
  ],
  "wifi": [
    {
      "source": "WiFi",
      "ssid": "HomeNetwork",
      "password": "wifipass123"
    }
  ]
}
```

---

## 🔧 Advanced Usage

### Mine Specific Sources

```python
from rt_registry_miner.miners import WiFiMiner, PuTTYMiner

# Use specific miner
wifi_miner = WiFiMiner()
credentials = wifi_miner.mine()

# Display results
for cred in credentials:
    print(f"{cred['ssid']}: {cred['password']}")
```

### Custom Output Directory

```python
miner = RegistryCredentialMiner(output_dir="/tmp/custom_output")
```

---

## 🛡️ OPSEC Considerations

### Detection Vectors

1. **Registry Access**: Accessing sensitive registry keys triggers alerts
2. **Tool Execution**: netsh, reg save commands logged
3. **File Creation**: Temporary registry hive files on disk
4. **Privilege Escalation**: PsExec or similar tools for SYSTEM access

### Privilege Requirements

| Miner | User | Admin | SYSTEM |
|-------|------|-------|--------|
| AutoLogon | ✗ | ✓ | ✓ |
| RDP | ✓ | ✓ | ✓ |
| WiFi | ✓ (own) | ✓ (all) | ✓ |
| PuTTY | ✓ | ✓ | ✓ |
| VNC | ✗ | ✓ | ✓ |
| WinSCP | ✓ | ✓ | ✓ |
| LSA Secrets | ✗ | ✗ | ✓ |

### Evasion Techniques

- **Selective Mining**: Only mine what you need
- **Cleanup**: Delete temporary files immediately
- **Timing**: Execute during maintenance windows
- **Alternative Tools**: Use living-off-the-land binaries

---

## 📚 Project Structure

```
rt_registry_miner_framework/
├── rt_registry_miner/
│   ├── __init__.py              # Package exports
│   ├── core.py                  # Main orchestrator
│   ├── cli.py                   # Command-line interface
│   ├── miners/                  # Individual miners
│   │   ├── __init__.py
│   │   ├── autologon.py         # AutoLogon miner
│   │   ├── rdp.py               # RDP miner
│   │   ├── wifi.py              # WiFi miner
│   │   ├── putty.py             # PuTTY miner
│   │   ├── vnc.py               # VNC miner
│   │   ├── winscp.py            # WinSCP miner
│   │   └── lsa_secrets.py       # LSA Secrets miner
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       ├── privileges.py        # Privilege checking
│       └── registry.py          # Registry utilities
├── examples/                    # Usage examples
│   ├── basic_mine.py
│   └── mine_all_sources.py
├── registry_mine.py            # Main CLI entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

---

## 🎓 Understanding Registry Credentials

### Why Registry?

The Windows registry is a goldmine for credentials because:

1. **AutoLogon**: Plaintext passwords for automatic logon
2. **Application Configs**: SSH/FTP/VNC clients store session info
3. **Cached Credentials**: Domain credentials cached locally
4. **Service Passwords**: Services running as domain accounts
5. **WiFi Profiles**: Saved network passwords

### Common Locations

| Credential Type | Registry Location |
|----------------|-------------------|
| AutoLogon | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` |
| RDP | `HKCU\Software\Microsoft\Terminal Server Client` |
| PuTTY | `HKCU\Software\SimonTatham\PuTTY\Sessions` |
| WinSCP | `HKCU\Software\Martin Prikryl\WinSCP 2\Sessions` |
| VNC | `HKLM\SOFTWARE\RealVNC\WinVNC4` (varies by version) |
| LSA Secrets | `HKLM\SECURITY\Policy\Secrets` |

---

## 🤝 Contributing

This framework is part of the "30 Days of Red Team" series. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📖 References

- [Windows Registry Documentation](https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry)
- [LSA Secrets Extraction](https://www.ired.team/offensive-security/credential-access-and-credential-dumping/dumping-lsa-secrets)
- [Impacket secretsdump](https://github.com/SecureAuthCorp/impacket)
- [PuTTY Registry Storage](https://the.earth.li/~sgtatham/putty/0.76/htmldoc/AppendixC.html)
- [30 Days of Red Team Series](https://medium.com/@maxwellcross)

---

## 📄 License

This project is for educational and authorized security testing purposes only.  
See LICENSE file for details.

---

**Happy Hunting! 🎯**  
*From the 30 Days of Red Team Series*
