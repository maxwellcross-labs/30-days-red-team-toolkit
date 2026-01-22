"""
Automated Lateral Movement Framework

A modular framework for automated lateral movement during
authorized penetration testing and red team operations.

Capabilities:
    - Credential spraying across targets
    - Access matrix generation
    - Automated command execution
    - Beacon deployment
    - Comprehensive reporting

Workflow:
    1. Test credentials against all targets
    2. Build access matrix showing valid combinations
    3. Execute commands on compromised systems
    4. Deploy C2 beacons for persistence
    5. Generate detailed reports

Basic Usage:
    from automated_lm_framework import AutomatedLateralMovement, Credential

    framework = AutomatedLateralMovement()

    # Manual workflow
    targets = framework.load_targets("targets.txt")
    credentials = framework.load_credentials("creds.txt")
    matrix = framework.test_credentials()
    chain = framework.execute_chain(matrix, "whoami")
    framework.deploy_beacons(matrix, "beacon.exe")
    framework.generate_report()

    # Or automated campaign
    framework.auto_campaign("targets.txt", "creds.txt", beacon="beacon.exe")

CLI Usage:
    python -m automated_lm_framework --targets hosts.txt --creds credentials.txt

Author: Maxwell Cross
Purpose: Authorized penetration testing and red team operations only.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

# Core exports
from .core import (
    AutomatedLateralMovement,
    Credential,
    AccessEntry,
    MovementStep,
    BeaconDeployment,
    AccessMatrix,
    MovementChain,
    FrameworkConfig,
    CredentialType,
    AccessLevel,
    ExecutionMethod
)

# Operations exports
from .operations import (
    CredentialTester,
    ChainExecutor,
    BeaconDeployer
)

# Report exports
from .reports import (
    ReportGenerator
)

# Utility exports
from .utils import (
    load_targets_from_file,
    load_credentials_from_file
)

__all__ = [
    # Version
    '__version__',
    '__author__',

    # Core
    'AutomatedLateralMovement',
    'Credential',
    'AccessEntry',
    'MovementStep',
    'BeaconDeployment',
    'AccessMatrix',
    'MovementChain',
    'FrameworkConfig',
    'CredentialType',
    'AccessLevel',
    'ExecutionMethod',

    # Operations
    'CredentialTester',
    'ChainExecutor',
    'BeaconDeployer',

    # Reports
    'ReportGenerator',

    # Utilities
    'load_targets_from_file',
    'load_credentials_from_file'
]