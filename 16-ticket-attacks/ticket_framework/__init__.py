"""
Pass-the-Ticket & Overpass-the-Hash Framework
Convert hashes to Kerberos tickets, inject and impersonate.
"""

__version__ = "1.0.0"
__author__ = "Maxwell Cross"

from .core.framework import TicketAttackFramework

__all__ = ["TicketAttackFramework"]