"""
Report Generator
================

Generate operation reports in various formats.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from ..models import AttackState


class ReportGenerator:
    """
    Generates reports for the attack operation.

    Supports:
    - Markdown reports
    - JSON exports
    - Executive summaries
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for report files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_markdown_report(self, state: AttackState, filename: str = "operation_report.md") -> Path:
        """
        Generate a comprehensive Markdown report.

        Args:
            state: Current attack state
            filename: Output filename

        Returns:
            Path to the generated report
        """
        report_path = self.output_dir / filename

        report = f"""# Week 3 Operation Report

## Operation Summary

| Metric | Value |
|--------|-------|
| Start Time | {state.operation_start.strftime("%Y-%m-%d %H:%M:%S")} |
| Report Generated | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
| Current Phase | {state.current_phase} |
| Systems Compromised | {state.system_count} |
| Credentials Harvested | {state.credential_count} |
| Active Pivots | {state.pivot_count} |
| Domains Compromised | {state.domain_count} |

---

## Phases Executed

### Phase 1: Privilege Escalation
- **Status:** {"Complete" if state.current_phase >= 1 else "Pending"}
- **Initial Access:** User-level
- **Final Access:** Admin/SYSTEM

### Phase 2: Credential Harvesting
- **Status:** {"Complete" if state.current_phase >= 2 else "Pending"}
- **Credentials Found:** {state.credential_count}
- **Sources:** LSASS, SAM, Registry, DPAPI

### Phase 3: Lateral Movement
- **Status:** {"Complete" if state.current_phase >= 3 else "Pending"}
- **Systems Compromised:** {state.system_count}
- **Methods:** Pass-the-Hash, WMI, PSRemoting

### Phase 4: Network Pivoting
- **Status:** {"Complete" if state.current_phase >= 4 else "Pending"}
- **Pivots Established:** {state.pivot_count}

### Phase 5: Domain/Trust Exploitation
- **Status:** {"Complete" if state.current_phase >= 5 else "Pending"}
- **Domains Compromised:** {state.domain_count}
- **Trust Relationships Found:** {len(state.trust_relationships)}

---

## Compromised Systems

| Hostname | IP Address | Platform | Privilege Level | Credentials Found |
|----------|------------|----------|-----------------|-------------------|
"""

        for system in state.compromised_systems:
            report += f"| {system.hostname} | {system.ip_address} | {system.platform.value} | {system.privilege_level.value} | {system.credential_count} |\n"

        if not state.compromised_systems:
            report += "| *No systems compromised yet* | - | - | - | - |\n"

        report += """
---

## Credential Summary

| Username | Domain | Has Password | Has Hash | Source |
|----------|--------|--------------|----------|--------|
"""

        for cred in state.all_credentials[:20]:  # Limit to first 20
            report += f"| {cred.username} | {cred.domain or 'LOCAL'} | {'Yes' if cred.has_password else 'No'} | {'Yes' if cred.has_hash else 'No'} | {cred.source} |\n"

        if not state.all_credentials:
            report += "| *No credentials harvested yet* | - | - | - | - |\n"

        if len(state.all_credentials) > 20:
            report += f"\n*... and {len(state.all_credentials) - 20} more credentials*\n"

        report += """
---

## Active Pivots

"""

        if state.active_pivots:
            for pivot in state.active_pivots:
                report += f"- **{pivot.get('pivot_host', 'Unknown')}** → {pivot.get('target_network', 'Unknown')}\n"
                report += f"  - Method: {pivot.get('method', 'Unknown')}\n"
                report += f"  - Local Port: {pivot.get('local_port', 'Unknown')}\n"
        else:
            report += "*No active pivots*\n"

        report += """
---

## Trust Relationships

"""

        if state.trust_relationships:
            for trust in state.trust_relationships:
                report += f"- {trust}\n"
        else:
            report += "*No trust relationships enumerated yet*\n"

        report += """
---

## Cleanup Required

- [ ] Remove persistence mechanisms
- [ ] Delete temporary files
- [ ] Clear artifacts on compromised systems
- [ ] Kill tunnel processes
- [ ] Remove uploaded tools
- [ ] Clear event logs (if authorized)

---

## Recommendations

*Based on the attack path, the following defensive improvements are recommended:*

1. **Credential Security**
   - Implement Credential Guard
   - Enable LSA protection
   - Reduce cached credentials

2. **Network Segmentation**
   - Review firewall rules
   - Implement microsegmentation
   - Monitor lateral movement patterns

3. **Trust Relationships**
   - Audit trust relationships
   - Enable SID filtering where possible
   - Implement selective authentication

4. **Monitoring**
   - Monitor LSASS access
   - Alert on DCSync activity
   - Track unusual authentication patterns

---

*Report generated by Week 3 Attack Orchestrator*
"""

        with open(report_path, "w") as f:
            f.write(report)

        return report_path

    def generate_json_export(self, state: AttackState, filename: str = "operation_state.json") -> Path:
        """
        Export the complete state as JSON.

        Args:
            state: Current attack state
            filename: Output filename

        Returns:
            Path to the generated JSON file
        """
        json_path = self.output_dir / filename

        with open(json_path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

        return json_path

    def generate_executive_summary(self, state: AttackState, filename: str = "executive_summary.md") -> Path:
        """
        Generate a brief executive summary.

        Args:
            state: Current attack state
            filename: Output filename

        Returns:
            Path to the generated summary
        """
        summary_path = self.output_dir / filename

        summary = f"""# Executive Summary

## Red Team Operation Results

**Duration:** {state.operation_start.strftime("%Y-%m-%d")} to {datetime.now().strftime("%Y-%m-%d")}

### Key Findings

- **{state.system_count}** systems compromised
- **{state.credential_count}** credentials harvested
- **{state.domain_count}** domains compromised
- **{len(state.trust_relationships)}** trust relationships identified

### Attack Path Summary

The operation began with initial access and progressed through privilege escalation, 
credential harvesting, lateral movement, network pivoting, and trust exploitation.

### Critical Observations

1. Credential harvesting yielded significant results, indicating potential 
   weaknesses in credential storage and protection.

2. Lateral movement was possible using harvested credentials, suggesting 
   insufficient network segmentation or monitoring.

3. Trust relationships provided paths to additional domains.

### Recommendations

Immediate actions should focus on:
- Credential protection improvements
- Network segmentation review
- Enhanced monitoring and detection

---

*This is a high-level summary. See the full report for details.*
"""

        with open(summary_path, "w") as f:
            f.write(summary)

        return summary_path