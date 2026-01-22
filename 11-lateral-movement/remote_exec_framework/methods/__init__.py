"""
Execution methods package for Remote Execution Framework
Provides factory function to get appropriate execution method
"""

import sys
from pathlib import Path
from typing import Dict, Type

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base import BaseExecutionMethod
from wmi import WMIExecutionMethod
from psremoting import PSRemotingExecutionMethod
from dcom import DCOMExecutionMethod
from beacon import BeaconDeployer

# Method registry for factory pattern
METHOD_REGISTRY: Dict[str, Type[BaseExecutionMethod]] = {
    'wmi': WMIExecutionMethod,
    'psremoting': PSRemotingExecutionMethod,
    'dcom': DCOMExecutionMethod
}


def get_execution_method(method_name: str, timeout: int = 30) -> BaseExecutionMethod:
    """
    Factory function to get execution method by name

    Args:
        method_name: Name of method ('wmi', 'psremoting', 'dcom')
        timeout: Command execution timeout

    Returns:
        Configured execution method instance

    Raises:
        ValueError: If method name is unknown
    """
    method_name = method_name.lower()

    if method_name not in METHOD_REGISTRY:
        valid_methods = ', '.join(METHOD_REGISTRY.keys())
        raise ValueError(f"Unknown method: {method_name}. Valid: {valid_methods}")

    return METHOD_REGISTRY[method_name](timeout=timeout)


def list_methods() -> list:
    """Get list of available method names"""
    return list(METHOD_REGISTRY.keys())


def get_beacon_deployer(timeout: int = 30) -> BeaconDeployer:
    """
    Get beacon deployer instance

    Args:
        timeout: Command execution timeout

    Returns:
        Configured BeaconDeployer instance
    """
    return BeaconDeployer(timeout=timeout)


__all__ = [
    'BaseExecutionMethod',
    'WMIExecutionMethod',
    'PSRemotingExecutionMethod',
    'DCOMExecutionMethod',
    'BeaconDeployer',
    'get_execution_method',
    'get_beacon_deployer',
    'list_methods',
    'METHOD_REGISTRY'
]