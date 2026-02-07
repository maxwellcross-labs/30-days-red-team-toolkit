# Active Directory Enumeration Framework

A modular Python framework for comprehensive Active Directory reconnaissance during red team operations.

## Features

- **Domain Information**: Enumerate domain controllers, DNS, and basic domain metadata
- **User Enumeration**: Identify all users, privileged accounts, and potential attack vectors
- **Group Enumeration**: Map group memberships with focus on privileged groups
- **Computer Enumeration**: Discover workstations, servers, and delegation vulnerabilities
- **SPN Discovery**: Identify Kerberoastable accounts
- **Trust Relationships**: Map domain trusts for lateral movement opportunities
- **Automated Reporting**: Generate JSON, text, and summary reports

## Attack Vectors Detected

✓ **Kerberoastable Users** - Users with SPNs for offline password cracking  
✓ **AS-REP Roastable Users** - Accounts without Kerberos pre-authentication  
✓ **Unconstrained Delegation** - Computers vulnerable to credential theft  
✓ **Constrained Delegation** - Potential privilege escalation paths  
✓ **LAPS Passwords** - Readable local admin passwords  
✓ **Passwords in Descriptions** - Cleartext credentials in user attributes  
✓ **Privileged Group Membership** - Domain Admins, Enterprise Admins, etc.

## Installation

```bash
# Install required dependencies
pip install ldap3

# Clone/download the framework
git clone <repository_url>
cd ad_enum_framework

# Make the main script executable
chmod +x ad_enum.py
```

## Usage

### Basic Enumeration
```bash
python3 ad_enum.py -d contoso.com -u jdoe -p Password123
```

### Specify Domain Controller
```bash
python3 ad_enum.py -d corp.local -u administrator -p Pass@123 --dc 10.0.0.10
```

### Custom Output Directory
```bash
python3 ad_enum.py -d lab.local -u admin -p P@ssw0rd -o ./recon_output
```

## Project Structure

```
ad_enum_framework/
├── ad_enum.py              # Main entry point
├── core/
│   ├── __init__.py
│   ├── config.py           # Configuration and constants
│   ├── connection.py       # LDAP connection handler
│   └── enumerator.py       # Main orchestrator
├── modules/
│   ├── __init__.py
│   ├── domain.py           # Domain info enumeration
│   ├── users.py            # User enumeration
│   ├── groups.py           # Group enumeration
│   ├── computers.py        # Computer enumeration
│   ├── spns.py             # SPN enumeration
│   └── trusts.py           # Trust enumeration
├── utils/
│   ├── __init__.py
│   └── reporter.py         # Report generation
└── output/                 # Default output directory
```

## Output Files

The framework generates multiple output files:

- `ad_enum_report.json` - Complete enumeration data in JSON format
- `users.txt` - Simple list of all domain users
- `kerberoastable.txt` - Users with SPNs for Kerberoasting
- `summary.txt` - Executive summary with key statistics

## Modular Architecture

### Core Components

**config.py** - Centralized configuration  
- Privileged group lists
- UAC flags
- LDAP attribute definitions
- Trust relationship mappings

**connection.py** - LDAP connection management  
- Establishes domain controller connections
- Handles authentication
- Manages connection lifecycle

**enumerator.py** - Main orchestrator  
- Initializes all modules
- Coordinates enumeration flow
- Aggregates results

### Enumeration Modules

Each module is independent and focused on a specific enumeration task:

- `domain.py` - Domain and DC enumeration
- `users.py` - User account discovery
- `groups.py` - Group membership mapping
- `computers.py` - Computer object enumeration
- `spns.py` - Service Principal Name discovery
- `trusts.py` - Trust relationship mapping

### Utilities

**reporter.py** - Multi-format report generation  
- JSON reports for programmatic access
- Text files for quick review
- Executive summaries for documentation

## Extending the Framework

To add new enumeration capabilities:

1. Create a new module in `modules/`
2. Implement the enumeration logic
3. Add the module to `core/enumerator.py`
4. Update `modules/__init__.py` to export the new module

Example:
```python
# modules/new_feature.py
class NewFeatureEnumerator:
    def __init__(self, ldap_conn):
        self.conn = ldap_conn.get_connection()
        self.base_dn = ldap_conn.get_base_dn()
    
    def enumerate(self):
        # Your enumeration logic
        return results
```

## OPSEC Considerations

⚠️ **This tool generates significant LDAP traffic**
- All queries are logged by domain controllers
- Defenders may detect unusual query patterns
- Use domain credentials that legitimately need this access
- Consider spreading enumeration over time
- Test detection rules in your own lab first

## Requirements

- Python 3.6+
- ldap3 library
- Valid domain credentials
- Network connectivity to domain controller

## Legal Notice

This tool is for authorized security testing only. Ensure you have explicit permission before running against any domain.

## Credits

Built for the "30 Days of Red Team" series