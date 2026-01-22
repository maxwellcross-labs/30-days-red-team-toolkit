"""
Core package for Automated Lateral Movement Framework
"""

from .models import (
    CredentialType,
    AccessLevel,
    ExecutionMethod,
    Credential,
    AccessEntry,
    MovementStep,
    BeaconDeployment,
    AccessMatrix,
    MovementChain,
    FrameworkConfig
)
from .framework import AutomatedLateralMovement

__all__ = [
    'CredentialType',
    'AccessLevel',
    'ExecutionMethod',
    'Credential',
    'AccessEntry',
    'MovementStep',
    'BeaconDeployment',
    'AccessMatrix',
    'MovementChain',
    'FrameworkConfig',
    'AutomatedLateralMovement'
]