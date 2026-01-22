"""
Remote Execution Framework

A modular framework for remote command execution during
authorized penetration testing and red team operations.

Supported Methods:
    - WMI via Impacket wmiexec (stealthy, supports hash)
    - PSRemoting via evil-winrm (interactive shell)
    - DCOM via Impacket dcomexec (alternative to WMI)

Features:
    - Single and multi-target execution
    - Beacon deployment capability
    - Interactive PSRemoting sessions
    - Both password and hash authentication
    - Professional JSON reporting

Basic Usage:
    from remote_exec_framework import RemoteExecutionFramework, Credential

    framework = RemoteExecutionFramework()
    credential = Credential("admin", password="Pass123", domain="CORP")

    # Execute command
    result = framework.execute(
        target="192.168.1.100",
        credential=credential,
        command="whoami",
        method="wmi"
    )

    # Multi-target
    results = framework.execute_on_multiple(
        targets=["192.168.1.100", "192.168.1.101"],
        credential=credential,
        command="hostname"
    )

    # Generate report
    framework.generate_report()

CLI Usage:
    python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --method wmi

Author: Maxwell Cross
Purpose: Authorized penetration testing and red team operations only.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

# Core exports
from .core import (
    RemoteExecutionFramework,
    Credential,
    ExecutionResult,
    MultiTargetResult,
    BeaconDeployResult,
    FrameworkConfig,
    ExecutionMethod,
    AuthType
)

# Method exports
from .methods import (
    get_execution_method,
    get_beacon_deployer,
    list_methods,
    WMIExecutionMethod,
    PSRemotingExecutionMethod,
    DCOMExecutionMethod,
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
    'RemoteExecutionFramework',
    'Credential',
    'ExecutionResult',
    'MultiTargetResult',
    'BeaconDeployResult',
    'FrameworkConfig',
    'ExecutionMethod',
    'AuthType',

    # Methods
    'get_execution_method',
    'get_beacon_deployer',
    'list_methods',
    'WMIExecutionMethod',
    'PSRemotingExecutionMethod',
    'DCOMExecutionMethod',
    'BeaconDeployer',

    # Reports
    'ReportGenerator',

    # Utilities
    'load_targets_from_file',
    'load_credentials_from_file'
]