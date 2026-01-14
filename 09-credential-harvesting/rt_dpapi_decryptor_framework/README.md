# DPAPI Decryptor Framework

**Windows DPAPI Credential Decryption Toolkit**  
Part of the *30 Days of Red Team* Series

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED SECURITY TESTING ONLY**

This tool is designed for authorized penetration testing and security research. Unauthorized access to computer systems is illegal. Users are responsible for complying with applicable laws and obtaining proper authorization before use.

---

## 🎯 Overview

A professional-grade DPAPI (Data Protection API) credential decryption framework that extracts and decrypts browser passwords, saved credentials, and Windows Vault data. Automates the discovery and decryption of credentials encrypted with Windows DPAPI.

### Key Features

- **5 Credential Decryptors**: Chrome, Edge, Firefox, Windows Vault, RDP
- **DPAPI Decryption**: Automatic decryption using Windows APIs
- **Professional Architecture**: Modular, extensible, production-ready
- **CLI & Library**: Use as command-line tool or Python library
- **Multiple Output Formats**: Text and JSON reports

---

## 📋 Requirements

- **OS**: Windows 10/11, Windows Server 2016+
- **Privileges**: Same user context as encrypted data
- **Python**: 3.8+
- **Dependencies**: pywin32 (for DPAPI)

---

## 🚀 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/dpapi_decryptor_framework.git
cd dpapi_decryptor_framework

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x dpapi_decrypt.py
```

### Package Install

```bash
# Install as package
pip install -e .

# Verify installation
python -c "import rt_dpapi_decryptor; print(dpapi_decryptor.__version__)"
```

---

## 💻 Usage

### Command-Line Interface

#### Basic Usage

```bash
# Check environment and availability
python dpapi_decrypt.py check

# Decrypt all credentials
python dpapi_decrypt.py decrypt --all

# Decrypt specific target
python dpapi_decrypt.py decrypt --target chrome
python dpapi_decrypt.py decrypt --target edge
```

#### List Available Decryptors

```bash
# List all decryptors
python dpapi_decrypt.py list

# Show only available decryptors
python dpapi_decrypt.py list --available

# Get detailed decryptor info
python dpapi_decrypt.py info --decryptor chrome
```

### Python Library Usage

#### Basic Decryption

```python
from rt_dpapi_decryptor import DPAPIDecryptor

# Initialize framework
decryptor = DPAPIDecryptor(output_dir="output")

# Decrypt Chrome passwords
chrome_creds = decryptor.decrypt_target('chrome')

# Display results
for cred in chrome_creds:
    print(f"{cred['url']}: {cred['username']} / {cred['password']}")
```

#### Comprehensive Decryption

```python
from rt_dpapi_decryptor import DPAPIDecryptor

decryptor = DPAPIDecryptor()

# Decrypt all sources
findings = decryptor.decrypt_all()

# Generate report
decryptor.generate_report(save_json=True)

# Access specific findings
if findings['chrome']:
    for cred in findings['chrome']:
        print(f"URL: {cred['url']}")
        print(f"User: {cred['username']}")
        print(f"Pass: {cred['password']}")
```

---

## 🎭 Credential Decryptors

### 1. Chrome Passwords

**Decrypt Google Chrome saved passwords**

- **Location**: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data`
- **Encryption**: DPAPI (user context)
- **Output**: URL, username, plaintext password

```bash
python dpapi_decrypt.py decrypt --target chrome
```

**How it works:**
1. Copies Chrome SQLite database (locked while running)
2. Queries saved passwords from `logins` table
3. Decrypts each password using DPAPI
4. Returns plaintext credentials

### 2. Microsoft Edge Passwords

**Decrypt Microsoft Edge saved passwords**

- **Location**: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data`
- **Encryption**: DPAPI (user context)
- **Output**: URL, username, plaintext password

```bash
python dpapi_decrypt.py decrypt --target edge
```

**Note**: Edge is Chromium-based and uses the same format as Chrome.

### 3. Firefox Passwords (Information Only)

**Extract Firefox password information**

- **Location**: `%APPDATA%\Mozilla\Firefox\Profiles`
- **Encryption**: NSS (NOT DPAPI)
- **Output**: URLs and metadata only

```bash
python dpapi_decrypt.py decrypt --target firefox
```

**Important**: Firefox uses NSS encryption, not DPAPI. This decryptor extracts metadata only. For actual decryption, use:
- **firefox_decrypt**: `https://github.com/unode/firefox_decrypt`
- Command: `firefox_decrypt.py`

### 4. Windows Credential Vault

**Extract Windows Credential Manager information**

- **Method**: vaultcmd.exe
- **Encryption**: DPAPI (requires additional tools for full decryption)
- **Output**: Credential metadata

```bash
python dpapi_decrypt.py decrypt --target windows_vault
```

**Note**: Passwords are DPAPI-encrypted. Full decryption requires:
- **mimikatz**: `vault::list`, `vault::cred`
- **SharpDPAPI**: `SharpDPAPI.exe vaults`

### 5. RDP Saved Credentials

**Extract RDP connection credentials**

- **Method**: cmdkey.exe
- **Location**: Windows Credential Manager
- **Output**: Connection targets

```bash
python dpapi_decrypt.py decrypt --target rdp
```

**Note**: Lists RDP targets only. Passwords require mimikatz or SharpDPAPI for decryption.

---

## 📊 Output Files

The framework generates comprehensive reports:

```
dpapi_creds/
├── dpapi_credentials.txt      # Human-readable report
├── dpapi_credentials.json     # Machine-readable JSON
├── chrome_temp.db             # Temporary (auto-deleted)
└── windows_vault.txt          # Vault output (if extracted)
```

### Credential Formats

**Chrome/Edge Format**:
```json
{
  "chrome": [
    {
      "source": "Chrome",
      "url": "https://example.com",
      "username": "user@example.com",
      "password": "P@ssw0rd123"
    }
  ]
}
```

**Windows Vault Format**:
```
Target: TERMSRV/192.168.1.100
Type: Domain:target=TERMSRV
User: administrator
```

---

## 🔧 Advanced Usage

### Custom Output Directory

```python
decryptor = DPAPIDecryptor(output_dir="/tmp/custom_output")
```

### Direct DPAPI Decryption

```python
from rt_dpapi_decryptor.utils import dpapi_decrypt, dpapi_decrypt_string

# Decrypt bytes
encrypted_data = b'...'
decrypted = dpapi_decrypt(encrypted_data)

# Decrypt to string
decrypted_str = dpapi_decrypt_string(encrypted_data)
```

### Check DPAPI Availability

```python
from rt_dpapi_decryptor.utils import is_dpapi_available

if is_dpapi_available():
    print("DPAPI ready")
else:
    print("Install pywin32")
```

---

## 🛡️ OPSEC Considerations

### Key Limitations

**User Context Required**: DPAPI can only decrypt data encrypted by the same user. If running as User A, you cannot decrypt User B's Chrome passwords.

**Active Processes**: Browser databases are locked while browsers are running. Copying the database solves this.

**Detection Vectors**:
1. **File Access**: Accessing browser databases triggers alerts
2. **Process Behavior**: Unusual process accessing SQLite databases
3. **Registry Access**: Windows Vault queries may be monitored
4. **Tool Execution**: vaultcmd, cmdkey execution logged

### Best Practices

```python
# 1. Run in same user context as target
whoami  # Verify user context

# 2. Decrypt quickly
decryptor = DPAPIDecryptor()
findings = decryptor.decrypt_all()

# 3. Clean up immediately
import os
os.remove("output/dpapi_credentials.txt")
os.remove("output/dpapi_credentials.json")
```

---

## 🎓 Understanding DPAPI

### What is DPAPI?

**DPAPI (Data Protection API)** is a Windows feature for encrypting and decrypting data using the user's login credentials:

- **User-Context Encryption**: Each user has unique DPAPI keys
- **Automatic Key Management**: Keys derived from user password
- **Transparent Decryption**: No password needed if same user

### What Uses DPAPI?

| Application | Data Encrypted |
|------------|----------------|
| Chrome | Saved passwords |
| Edge | Saved passwords |
| Windows Vault | Generic credentials |
| RDP | Connection passwords |
| Outlook | Email passwords |
| Internet Explorer | Saved passwords |

### DPAPI Protection Levels

**Local User**: Data encrypted with user's password
- Survives reboots
- Tied to user SID
- Cannot decrypt if user password changes (without migration)

**Machine-Level**: Data encrypted with machine key
- Any user on machine can decrypt
- Used by services

---

## 📚 Project Structure

```
rt_dpapi_decryptor_framework/
├── rt_dpapi_decryptor/
│   ├── __init__.py              # Package exports
│   ├── core.py                  # Main orchestrator
│   ├── cli.py                   # Command-line interface
│   ├── decryptors/              # Individual decryptors
│   │   ├── __init__.py
│   │   ├── chrome.py            # Chrome decryptor
│   │   ├── edge.py              # Edge decryptor
│   │   ├── firefox.py           # Firefox extractor
│   │   ├── windows_vault.py     # Windows Vault
│   │   └── rdp.py               # RDP credentials
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       ├── privileges.py        # Privilege checking
│       └── dpapi.py             # DPAPI utilities
├── examples/                    # Usage examples
│   ├── basic_decrypt.py
│   └── decrypt_all_browsers.py
├── dpapi_decrypt.py            # Main CLI entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

---

## 🤝 Contributing

This framework is part of the "30 Days of Red Team" series. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📖 References

- [Windows DPAPI](https://docs.microsoft.com/en-us/windows/win32/api/dpapi/)
- [Chrome Password Storage](https://chromium.googlesource.com/chromium/src/+/master/docs/security/password-storage.md)
- [Firefox NSS](https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS)
- [mimikatz DPAPI](https://github.com/gentilkiwi/mimikatz/wiki/module-~-dpapi)
- [SharpDPAPI](https://github.com/GhostPack/SharpDPAPI)
- [30 Days of Red Team Series](https://medium.com/@maxwellcross)

---

## 📄 License

This project is for educational and authorized security testing purposes only.  
See LICENSE file for details.

---

**Happy Hunting! 🎯**  
*From the 30 Days of Red Team Series*
