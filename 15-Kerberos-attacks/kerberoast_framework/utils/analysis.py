"""
Password Age Analyzer — Prioritize targets by password age.

Older passwords have higher crack probability due to weaker
password policies in effect at time of creation.
"""

from datetime import datetime
from typing import List, Dict

from ..core.target import RoastingTarget


class PasswordAgeAnalyzer:
    """Bucket targets by password age for prioritized cracking."""

    BUCKETS = ["5+ years", "2-5 years", "1-2 years", "< 1 year"]

    def analyze(self, targets: List[RoastingTarget]) -> Dict[str, List[RoastingTarget]]:
        """Group targets into age buckets and print analysis."""
        print("\n[*] Password Age Analysis (Older = Higher Crack Probability)...")

        now = datetime.now()
        age_buckets: Dict[str, List[RoastingTarget]] = {b: [] for b in self.BUCKETS}

        for target in targets:
            bucket = self._classify(target, now)
            if bucket:
                age_buckets[bucket].append(target)

        for bucket, accounts in age_buckets.items():
            if accounts:
                print(f"\n    [{bucket}] ({len(accounts)} accounts)")
                for acct in accounts:
                    admin_tag = " [ADMIN]" if acct.is_admin else ""
                    print(f"        {acct.username}{admin_tag} ({acct.roast_type})")

        print("\n[*] Target 5+ year old passwords first — highest crack probability")
        return age_buckets

    @staticmethod
    def _classify(target: RoastingTarget, now: datetime) -> str:
        """Return the age bucket string for a target, or empty if unparseable."""
        try:
            raw = target.pwd_last_set
            if not raw or raw in ("", "[]", "0"):
                return ""
            pwd_set = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
            age_years = (now - pwd_set).days / 365.25

            if age_years > 5:
                return "5+ years"
            if age_years > 2:
                return "2-5 years"
            if age_years > 1:
                return "1-2 years"
            return "< 1 year"
        except (ValueError, TypeError):
            return ""