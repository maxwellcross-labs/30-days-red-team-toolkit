"""
Scheduled Task Exploitation Framework
=====================================

A modular framework for enumerating and exploiting Windows scheduled task
misconfigurations for privilege escalation.

Features:
    - Enumerate all scheduled tasks
    - Identify tasks running as SYSTEM/Administrator
    - Check for writable task scripts and executables
    - Exploit writable tasks while maintaining functionality
    - Automatic backup and restoration
    - OPSEC-conscious cleanup
    - Timestamp preservation

Modules:
    - core: Task enumeration and analysis
    - exploits: Script injection and exploitation
    - utils: Helper functions and reporting

Author: Red Team Operations
Version: 1.0.0
"""

from .core.enumerator import TaskEnumerator
from .core.analyzer import TaskAnalyzer
from .exploits.script_injector import ScriptInjector
from .exploits.task_exploiter import TaskExploiter

__version__ = "1.0.0"
__all__ = [
    "TaskEnumerator",
    "TaskAnalyzer",
    "ScriptInjector",
    "TaskExploiter"
]
