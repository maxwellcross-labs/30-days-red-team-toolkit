"""
High-Value Target Analyzer
Identify and categorize high-value lateral movement targets
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    HostInfo,
    TargetCategory,
    TargetCollection,
    HIGH_VALUE_KEYWORDS
)
from ..utils.output import output


class HighValueAnalyzer:
    """
    Analyze discovered hosts to identify high-value targets

    High-value targets include:
        - Domain Controllers (keys to the kingdom)
        - File Servers (data exfiltration)
        - Database Servers (sensitive data)
        - Mail Servers (credentials, sensitive comms)
        - Backup Servers (often have elevated access)

    Identification is based on:
        - Hostname patterns
        - Service banners
        - Network role
    """

    def __init__(self):
        self.keywords = HIGH_VALUE_KEYWORDS

    def analyze_host(self, host: HostInfo) -> List[TargetCategory]:
        """
        Analyze single host for high-value indicators

        Args:
            host: HostInfo to analyze

        Returns:
            List of identified categories
        """
        categories = []

        # Build searchable text from host info
        search_text = ""

        if host.hostname:
            search_text += host.hostname.upper() + " "

        if host.raw_output:
            search_text += host.raw_output.upper()

        if not search_text:
            return categories

        # Check against keywords
        for keyword, category in self.keywords:
            if keyword in search_text:
                if category not in categories:
                    categories.append(category)

        # If any special category found, also mark as high-value
        special_categories = [
            TargetCategory.DOMAIN_CONTROLLER,
            TargetCategory.DATABASE,
            TargetCategory.MAIL_SERVER,
            TargetCategory.BACKUP_SERVER
        ]

        if any(cat in categories for cat in special_categories):
            if TargetCategory.HIGH_VALUE not in categories:
                categories.append(TargetCategory.HIGH_VALUE)

        return categories

    def analyze_collection(self, collection: TargetCollection) -> int:
        """
        Analyze all hosts in collection for high-value targets

        Args:
            collection: TargetCollection to analyze

        Returns:
            Number of high-value targets identified
        """
        output.info("Identifying high-value targets...")

        high_value_count = 0

        for ip, host in collection.all_hosts.items():
            categories = self.analyze_host(host)

            for category in categories:
                host.add_category(category)

                # Update collection categories
                if category == TargetCategory.DOMAIN_CONTROLLER:
                    collection.domain_controllers[ip] = host

                if category == TargetCategory.HIGH_VALUE:
                    if ip not in collection.high_value:
                        collection.high_value[ip] = host
                        high_value_count += 1

                        # Log the finding
                        reason = categories[0].value if categories else "Pattern match"
                        output.success(f"High-value target: {ip} ({reason})")

        output.newline()
        output.success(f"Identified {len(collection.high_value)} high-value targets")

        return high_value_count