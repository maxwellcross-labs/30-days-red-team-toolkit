"""
Module Entry Point
==================

Allows running the package directly:
    python -m week3_orchestrator
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())