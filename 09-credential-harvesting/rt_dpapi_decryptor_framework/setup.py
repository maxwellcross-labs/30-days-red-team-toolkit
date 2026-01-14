#!/usr/bin/env python3
"""
Setup script for DPAPI Decryptor Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="dpapi-decryptor-framework",
    version="1.0.0",
    author="30 Days of Red Team",
    description="DPAPI credential decryption framework for browser passwords and saved credentials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dpapi_decryptor_framework",
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
        "pywin32>=305",
    ],
    extras_require={
        "firefox": ["firefox-decrypt"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dpapi-decrypt=rt_dpapi_decryptor.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
