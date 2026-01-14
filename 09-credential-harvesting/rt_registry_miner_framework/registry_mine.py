#!/usr/bin/env python3
"""
Registry Credential Miner Framework - Main Entry Point
Windows registry credential extraction toolkit

WARNING: For authorized security testing only
Unauthorized access to computer systems is illegal
"""

import sys
from rt_registry_miner.cli import main

if __name__ == '__main__':
    sys.exit(main())
