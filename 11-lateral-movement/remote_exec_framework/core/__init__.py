"""
Core package for Remote Execution Framework
"""

from .models import (
    ExecutionMethod,
    AuthType,
    Credential,
    ExecutionResult,
    MultiTargetResult,
    BeaconDeployResult,
    FrameworkConfig
)
from .framework import RemoteExecutionFramework

__all__ = [
    'ExecutionMethod',
    'AuthType',
    'Credential',
    'ExecutionResult',
    'MultiTargetResult',
    'BeaconDeployResult',
    'FrameworkConfig',
    'RemoteExecutionFramework'
]
