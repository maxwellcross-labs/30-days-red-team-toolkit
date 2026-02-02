"""
Week 3 Orchestrator
===================

Main orchestrator that chains all attack phases together.
"""

from pathlib import Path
from typing import List, Optional

from ..models import (
    Platform,
    PrivilegeLevel,
    Credential,
    CompromisedSystem,
    AttackState,
)
from ..phases import (
    PrivilegeEscalationPhase,
    CredentialHarvestingPhase,
    LateralMovementPhase,
    PivotingPhase,
    TrustExploitationPhase,
)
from .logger import OperationLogger
from .reporter import ReportGenerator


class Week3Orchestrator:
    """
    Master orchestrator for Week 3 attack chain.

    Integrates all techniques into a seamless workflow:
    1. Privilege Escalation
    2. Credential Harvesting
    3. Lateral Movement
    4. Network Pivoting
    5. Domain & Trust Exploitation
    """

    BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         WEEK 3 INTEGRATED ATTACK ORCHESTRATOR                ║
║                                                              ║
║  Credential Harvesting → Privilege Escalation →              ║
║  Lateral Movement → Pivoting → Trust Exploitation            ║
╚══════════════════════════════════════════════════════════════╝
"""

    def __init__(self, output_dir: str = "week3_operation"):
        """
        Initialize the orchestrator.

        Args:
            output_dir: Directory for all output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize components
        self.state = AttackState()
        self.logger = OperationLogger(self.output_dir)
        self.reporter = ReportGenerator(self.output_dir)

        # Initialize phases
        self.phases = {
            1: PrivilegeEscalationPhase(self.state, self.logger),
            2: CredentialHarvestingPhase(self.state, self.logger),
            3: LateralMovementPhase(self.state, self.logger),
            4: PivotingPhase(self.state, self.logger),
            5: TrustExploitationPhase(self.state, self.logger),
        }

        # Print banner
        print(self.BANNER)
        self.logger.info(f"Output directory: {self.output_dir}")

    def phase1_privilege_escalation(self, platform: Platform) -> bool:
        """
        Execute Phase 1: Privilege Escalation

        Args:
            platform: Target platform (WINDOWS or LINUX)

        Returns:
            True if successful
        """
        system = CompromisedSystem(
            hostname="initial-target",
            ip_address="unknown",
            platform=platform,
            privilege_level=PrivilegeLevel.USER,
        )

        result = self.phases[1].execute(system)

        if result:
            system.privilege_level = PrivilegeLevel.ADMIN if platform == Platform.WINDOWS else PrivilegeLevel.ROOT
            self.state.initial_system = system
            self.state.add_system(system)
            self.state.current_phase = 1

        return result

    def phase2_credential_harvesting(self, system: Optional[CompromisedSystem] = None) -> List[Credential]:
        """
        Execute Phase 2: Credential Harvesting

        Args:
            system: System to harvest from (defaults to initial system)

        Returns:
            List of harvested credentials
        """
        if system is None:
            system = self.state.initial_system

        if system is None:
            self.logger.error("No system available for credential harvesting")
            return []

        credentials = self.phases[2].execute(system)
        self.state.current_phase = max(self.state.current_phase, 2)

        return credentials

    def phase3_lateral_movement(self, credentials: Optional[List[Credential]] = None,
                                targets: Optional[List[str]] = None) -> List[CompromisedSystem]:
        """
        Execute Phase 3: Lateral Movement

        Args:
            credentials: Credentials to use (defaults to all harvested)
            targets: Target hosts/networks

        Returns:
            List of newly compromised systems
        """
        if credentials is None:
            credentials = self.state.all_credentials

        if targets is None:
            targets = ["192.168.1.0/24"]

        newly_compromised = self.phases[3].execute(credentials, targets)
        self.state.current_phase = max(self.state.current_phase, 3)

        return newly_compromised

    def phase4_network_pivoting(self, pivot_host: Optional[CompromisedSystem] = None,
                                target_network: str = "10.0.0.0/24") -> bool:
        """
        Execute Phase 4: Network Pivoting

        Args:
            pivot_host: System to use as pivot (defaults to initial)
            target_network: Network to access through pivot

        Returns:
            True if pivot established
        """
        if pivot_host is None:
            pivot_host = self.state.initial_system

        if pivot_host is None:
            self.logger.error("No pivot host available")
            return False

        result = self.phases[4].execute(pivot_host, target_network)
        self.state.current_phase = max(self.state.current_phase, 4)

        return result

    def phase5_domain_trust_exploitation(self, domain_admin_creds: Optional[Credential] = None,
                                         domain: str = "CORP.LOCAL") -> bool:
        """
        Execute Phase 5: Domain & Trust Exploitation

        Args:
            domain_admin_creds: Domain admin credentials
            domain: Target domain

        Returns:
            True if successful
        """
        if domain_admin_creds is None:
            # Try to find domain admin creds in harvested
            da_creds = self.state.get_domain_admin_credentials()
            if da_creds:
                domain_admin_creds = da_creds[0]
            else:
                domain_admin_creds = Credential(
                    username="domainadmin",
                    domain="CORP",
                )

        result = self.phases[5].execute(domain_admin_creds, domain)
        self.state.current_phase = max(self.state.current_phase, 5)

        return result

    def execute_full_chain(self, initial_platform: Platform,
                           targets: Optional[List[str]] = None) -> None:
        """
        Execute the complete Week 3 attack chain.

        Args:
            initial_platform: Platform of initial compromised system
            targets: Target networks/hosts for lateral movement
        """
        self.logger.header("EXECUTING COMPLETE WEEK 3 ATTACK CHAIN")

        targets = targets or ["192.168.1.0/24"]

        # Phase 1
        self.phase1_privilege_escalation(initial_platform)

        # Phase 2
        credentials = self.phase2_credential_harvesting()

        # Phase 3
        self.phase3_lateral_movement(credentials, targets)

        # Phase 4
        self.phase4_network_pivoting()

        # Phase 5
        self.phase5_domain_trust_exploitation()

        # Generate reports
        self.generate_reports()

    def execute_phase(self, phase_number: int, **kwargs) -> bool:
        """
        Execute a specific phase.

        Args:
            phase_number: Phase to execute (1-5)
            **kwargs: Phase-specific arguments

        Returns:
            True if phase completed successfully
        """
        if phase_number not in self.phases:
            self.logger.error(f"Invalid phase number: {phase_number}")
            return False

        phase_methods = {
            1: lambda: self.phase1_privilege_escalation(kwargs.get("platform", Platform.WINDOWS)),
            2: lambda: self.phase2_credential_harvesting(kwargs.get("system")),
            3: lambda: self.phase3_lateral_movement(kwargs.get("credentials"), kwargs.get("targets")),
            4: lambda: self.phase4_network_pivoting(kwargs.get("pivot_host"),
                                                    kwargs.get("target_network", "10.0.0.0/24")),
            5: lambda: self.phase5_domain_trust_exploitation(kwargs.get("domain_admin_creds"),
                                                             kwargs.get("domain", "CORP.LOCAL")),
        }

        return phase_methods[phase_number]()

    def generate_reports(self) -> None:
        """Generate all reports"""
        self.logger.info("Generating reports...")

        # Markdown report
        report_path = self.reporter.generate_markdown_report(self.state)
        self.logger.success(f"Markdown report: {report_path}")

        # JSON export
        json_path = self.reporter.generate_json_export(self.state)
        self.logger.success(f"JSON export: {json_path}")

        # Executive summary
        summary_path = self.reporter.generate_executive_summary(self.state)
        self.logger.success(f"Executive summary: {summary_path}")

        # Save JSON log
        self.logger.save_json_log()
        self.logger.success("Operation complete")

    def get_state_summary(self) -> str:
        """Get a summary of the current state"""
        return self.state.summary()

    def save_state(self, filename: str = "state.json") -> Path:
        """Save current state to file"""
        return self.reporter.generate_json_export(self.state, filename)

    def load_state(self, filepath: str) -> None:
        """Load state from file"""
        import json
        with open(filepath) as f:
            data = json.load(f)
        self.state = AttackState.from_dict(data)
        self.logger.info(f"State loaded from {filepath}")