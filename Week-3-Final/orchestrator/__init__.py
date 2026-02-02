"""
Week 3 Integrated Attack Orchestrator
=====================================

A modular framework for chaining red team techniques:
- Privilege Escalation
- Credential Harvesting
- Lateral Movement
- Network Pivoting
- Trust Exploitation

Usage:
    from week3_orchestrator import Week3Orchestrator, Platform

    orchestrator = Week3Orchestrator(output_dir="my_operation")
    orchestrator.execute_full_chain(Platform.WINDOWS)
"""

__version__ = "1.0.0"
__author__ = "Red Team Operator"

from .models import (
    Platform,
    PrivilegeLevel,
    Credential,
    CompromisedSystem,
    AttackState,
)

from .core.orchestrator import Week3Orchestrator

__all__ = [
    "Week3Orchestrator",
    "Platform",
    "PrivilegeLevel",
    "Credential",
    "CompromisedSystem",
    "AttackState",
]