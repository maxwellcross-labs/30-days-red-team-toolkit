#!/usr/bin/env python3
"""
Setup script for Registry Credential Miner Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="registry-credential-miner",
    version="1.0.0",
    author="30 Days of Red Team",
    description="Windows registry credential extraction framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/registry_miner_framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Optional: impacket for LSA secrets
    ],
    extras_require={
        "lsa": ["impacket>=0.11.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "registry-mine=rt_registry_miner.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
