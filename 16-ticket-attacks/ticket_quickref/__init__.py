"""
Ticket Attack Quick Reference — Decision tree and instant commands.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

from .decision_tree import print_ticket_decision_tree
from .service_reference import print_silver_ticket_services
from .format_reference import print_ticket_format_conversion

__all__ = [
    "print_ticket_decision_tree",
    "print_silver_ticket_services",
    "print_ticket_format_conversion",
]