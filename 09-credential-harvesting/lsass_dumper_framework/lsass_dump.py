#!/usr/bin/env python3
"""
LSASS Dumper Framework - Main Entry Point
Multi-method credential harvesting toolkit

WARNING: For authorized security testing only
Unauthorized access to computer systems is illegal
"""

import sys
from lsass_dumper.cli import main

if __name__ == '__main__':
    sys.exit(main())
