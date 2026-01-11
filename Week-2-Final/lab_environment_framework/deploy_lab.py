#!/usr/bin/env python3
"""
Lab Deployment Script
Quick deployment of red team lab environment
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lab_environment import LabDeployer


def main():
    """Main deployment function"""
    deployer = LabDeployer(lab_name="red-team-lab")
    deployer.deploy_lab()


if __name__ == "__main__":
    main()
