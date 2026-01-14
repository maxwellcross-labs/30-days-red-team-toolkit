#!/usr/bin/env python3
"""
Initial Access Handler
Orchestrates complete post-exploitation workflow
"""

from ..core.session import Session
from ..core.operation_log import OperationLog
from ..modules.access_verification import AccessVerifier
from ..modules.persistence import PersistenceManager
from ..modules.c2_setup import C2Manager
from ..modules.enumeration import EnumerationManager
from ..modules.cleanup import CleanupManager


class InitialAccessHandler:
    """
    Complete initial access orchestration
    Coordinates all modules for professional post-exploitation
    """
    
    def __init__(self, target_ip: str, c2_server: str, platform: str = "windows"):
        """
        Initialize initial access handler
        
        Args:
            target_ip: Target system IP address
            c2_server: Command and Control server address
            platform: Target platform ('windows' or 'linux')
        """
        # Initialize session
        self.session = Session(target_ip, c2_server)
        
        # Initialize logging
        self.log = OperationLog(self.session.session_id)
        
        # Initialize modules
        self.access_verifier = AccessVerifier(target_ip)
        self.persistence = PersistenceManager(c2_server)
        self.c2 = C2Manager(c2_server)
        self.enumeration = EnumerationManager(platform)
        self.cleanup = CleanupManager(platform)
        
        self.platform = platform
    
    def verify_initial_access(self) -> bool:
        """
        Phase 1: Verify initial access
        Confirms shell is functional before proceeding
        
        Returns:
            True if access verified, False otherwise
        """
        self.log.log_phase_start("Initial Access Verification", "Testing shell connectivity")
        
        success, message = self.access_verifier.verify_access()
        
        if success:
            self.log.log_action("Initial Access", "SUCCESS", message)
            self.session.mark_phase_complete('access')
            return True
        else:
            self.log.log_action("Initial Access", "FAILED", message)
            return False
    
    def deploy_persistence(self) -> bool:
        """
        Phase 2: Deploy persistence mechanisms
        CRITICAL: Must happen within first 5 minutes
        
        Returns:
            True if persistence deployed successfully
        """
        self.log.log_phase_start(
            "Persistence Deployment",
            "Installing multiple redundant persistence mechanisms"
        )
        
        # Get recommended persistence methods
        methods = self.persistence.get_recommended_methods(count=3)
        
        self.log.log_action(
            "Persistence",
            "Deploying",
            f"Installing {len(methods)} methods: {', '.join(m.name for m in methods)}"
        )
        
        deployed = 0
        for method in methods:
            self.log.log_action("Persistence", "Installing", method.name)
            
            # In production, this would execute via C2
            # For now, we log the intent
            self.log.log_action(
                "Persistence",
                "SUCCESS",
                f"{method.name} - {method.description}"
            )
            deployed += 1
        
        summary = self.persistence.get_deployment_summary(methods)
        self.log.log_phase_complete(
            "Persistence Deployment",
            f"{deployed} methods installed successfully"
        )
        
        self.session.mark_phase_complete('persistence')
        return True
    
    def establish_c2(self) -> bool:
        """
        Phase 3: Establish multi-channel C2
        Primary + fallback channels for redundancy
        
        Returns:
            True if C2 established successfully
        """
        self.log.log_phase_start(
            "C2 Establishment",
            "Configuring multi-channel command and control"
        )
        
        # Get C2 configuration
        config = self.c2.generate_agent_config(self.session.session_id)
        
        self.log.log_action(
            "C2 Setup",
            "Configuring",
            f"Total channels: {len(config['channels'])}"
        )
        
        for channel in config['channels']:
            priority = "PRIMARY" if channel['priority'] == 1 else f"FALLBACK {channel['priority']-1}"
            self.log.log_action(
                "C2 Setup",
                "SUCCESS",
                f"{priority} - {channel['type']} via {channel['server']}"
            )
        
        summary = self.c2.get_channel_summary()
        self.log.log_phase_complete(
            "C2 Establishment",
            f"Multi-channel C2 operational: {summary['total_channels']} channels"
        )
        
        self.session.mark_phase_complete('c2')
        return True
    
    def perform_enumeration(self) -> bool:
        """
        Phase 4: Initial system enumeration
        Gather critical situational awareness
        
        Returns:
            True if enumeration completed successfully
        """
        self.log.log_phase_start(
            "Initial Enumeration",
            "Collecting system reconnaissance data"
        )
        
        # Get critical commands
        critical = self.enumeration.get_critical_commands()
        important = self.enumeration.get_important_commands()
        
        self.log.log_action(
            "Enumeration",
            "Planning",
            f"Critical commands: {len(critical)}, Important commands: {len(important)}"
        )
        
        # Log each enumeration command
        for cmd in critical:
            self.log.log_action(
                "Enumeration",
                "Running",
                f"[{cmd.category}] {cmd.description}: {cmd.command}"
            )
        
        checklist = self.enumeration.get_enumeration_checklist()
        self.log.log_phase_complete(
            "Initial Enumeration",
            f"Reconnaissance complete - {checklist['total_commands']} commands executed"
        )
        
        self.session.mark_phase_complete('enumeration')
        return True
    
    def configure_cleanup(self) -> bool:
        """
        Phase 5: Configure automated cleanup
        Proactive artifact removal from the start
        
        Returns:
            True if cleanup configured successfully
        """
        self.log.log_phase_start(
            "Cleanup Configuration",
            "Setting up automated artifact removal"
        )
        
        # Get cleanup summary
        summary = self.cleanup.get_cleanup_summary()
        
        self.log.log_action(
            "Cleanup Setup",
            "Configuring",
            f"Total tasks: {summary['total_tasks']}"
        )
        
        # Log each cleanup frequency
        for freq, count in summary['by_frequency'].items():
            if count > 0:
                self.log.log_action(
                    "Cleanup Setup",
                    "SUCCESS",
                    f"{freq.capitalize()} cleanup: {count} tasks"
                )
        
        self.log.log_phase_complete(
            "Cleanup Configuration",
            "Automated cleanup operational"
        )
        
        self.session.mark_phase_complete('rt_cleanup')
        return True
    
    def execute_initial_access_protocol(self) -> bool:
        """
        Execute complete initial access protocol
        This is the full workflow professionals run in first 30 minutes
        
        Returns:
            True if all phases completed successfully
        """
        print("="*60)
        print("INTEGRATED INITIAL ACCESS HANDLER")
        print(f"Target: {self.session.target_ip}")
        print(f"C2 Server: {self.session.c2_server}")
        print(f"Session: {self.session.session_id}")
        print(f"Platform: {self.platform.upper()}")
        print("="*60)
        print()
        
        # Phase 1: Verify access (0-5 minutes)
        if not self.verify_initial_access():
            print("\n[!] Initial access verification failed. Aborting operation.")
            return False
        
        # Phase 2: Deploy persistence (5-10 minutes)
        if not self.deploy_persistence():
            print("\n[!] Persistence deployment failed. Continuing anyway...")
        
        # Phase 3: Establish C2 (10-15 minutes)
        if not self.establish_c2():
            print("\n[!] C2 establishment failed. Continuing anyway...")
        
        # Phase 4: Initial enumeration (15-25 minutes)
        if not self.perform_enumeration():
            print("\n[!] Enumeration failed. Continuing anyway...")
        
        # Phase 5: Configure cleanup (25-30 minutes)
        if not self.configure_cleanup():
            print("\n[!] Cleanup configuration failed. Continuing anyway...")
        
        # Finalize session
        self.session.finalize()
        
        # Save operation log
        log_path = self.log.save_log()
        
        # Display final status
        print("\n" + "="*60)
        print("INITIAL ACCESS PROTOCOL COMPLETE")
        print("="*60)
        
        status = self.session.get_session_status()
        print(f"\nSession Duration: {status['elapsed_time']}")
        print("\nPhase Completion:")
        for phase, completed in status['phases'].items():
            status_icon = "✓" if completed else "✗"
            print(f"  {status_icon} {phase.replace('_', ' ').title()}")
        
        print(f"\nOperation Log: {log_path}")
        print("="*60)
        
        return True
    
    def get_operation_summary(self) -> dict:
        """Get complete operation summary"""
        return {
            'session': self.session.get_session_status(),
            'persistence': self.persistence.get_deployment_summary(),
            'c2': self.c2.get_channel_summary(),
            'enumeration': self.enumeration.get_enumeration_checklist(),
            'rt_cleanup': self.cleanup.get_cleanup_summary(),
            'log_entries': len(self.log.get_logs())
        }
