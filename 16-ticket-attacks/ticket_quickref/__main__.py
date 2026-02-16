#!/usr/bin/env python3
"""
CLI Entry Point — Ticket Attack Quick Reference

Usage:
    python -m ticket_quickref              # Print everything
    python -m ticket_quickref --tree       # Decision tree only
    python -m ticket_quickref --services   # Silver Ticket SPNs only
    python -m ticket_quickref --formats    # Format conversion only
"""

import argparse

from .decision_tree import print_ticket_decision_tree
from .service_reference import print_silver_ticket_services
from .format_reference import print_ticket_format_conversion


def main():
    parser = argparse.ArgumentParser(
        description="Ticket Attack Quick Reference"
    )
    parser.add_argument("--tree", action="store_true", help="Decision tree only")
    parser.add_argument("--services", action="store_true", help="Silver Ticket SPNs only")
    parser.add_argument("--formats", action="store_true", help="Format conversion only")

    args = parser.parse_args()

    # If no flags, print everything
    if not (args.tree or args.services or args.formats):
        print_ticket_decision_tree()
        print_silver_ticket_services()
        print_ticket_format_conversion()
        return

    if args.tree:
        print_ticket_decision_tree()
    if args.services:
        print_silver_ticket_services()
    if args.formats:
        print_ticket_format_conversion()


if __name__ == "__main__":
    main()