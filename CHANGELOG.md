# Changelog

All notable changes to the **30 Days of Red Team Toolkit** are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/).

---

## [4.0.0] — 2026-02-16 (Days 22–24: Active Directory & Domain Dominance)

### Added — Day 22: Active Directory Enumeration
- `14-ad-enumeration/ad_enum_framework/` — Python LDAP-based AD enumeration
  - `modules/spns.py` — SPN discovery for Kerberoasting target identification
  - `utils/reporter.py` — Multi-format reporting (JSON, text, executive summary)
  - Domain info, user, group, computer, trust, and delegation enumeration
  - Automatic attack surface mapping: Kerberoastable users, AS-REP Roastable accounts, unconstrained delegation, LAPS exposure, passwords in descriptions, critical ACL misconfigurations
- `14-ad-enumeration/powerview_enum_framework/` — PowerView-based Windows enumeration
  - `utils/Reporter.ps1` — PowerShell reporting with attack path analysis

### Added — Day 23: Kerberoasting & AS-REP Roasting
- `15-Kerberos-attacks/kerberoast_framework/` — Complete roasting framework
  - `core/framework.py` — Main orchestrator: enumerate → request → extract → crack
  - `core/target.py` — RoastingTarget data model with priority scoring
  - `core/enumerator.py` — LDAP-based target discovery
  - `extractors/kerberoast.py` — TGS ticket extraction via Impacket
  - `extractors/asreproast.py` — AS-REP hash extraction for pre-auth disabled accounts
  - `utils/analysis.py` — Password age analysis for target prioritization
  - `utils/cracking.py` — Hashcat command generation and optimization
  - `utils/reporting.py` — Comprehensive roasting operation reports

### Added — Day 24: Pass-the-Ticket & Overpass-the-Hash
- `16-ticket-attacks/ticket_framework/` — Complete Kerberos ticket attack framework
  - `core/framework.py` — TicketAttackFramework orchestrator
  - `core/sid_resolver.py` — Domain SID resolution via LDAP/Impacket
  - `attacks/overpass.py` — Overpass-the-Hash (NTLM hash → Kerberos TGT)
  - `attacks/pass_ticket.py` — Pass-the-Ticket injection and impersonation
  - `attacks/golden.py` — Golden Ticket forging with KRBTGT hash
  - `attacks/silver.py` — Silver Ticket forging with service account hash
  - `attacks/diamond.py` — Diamond Ticket guidance (TGT modification)
  - `utils/ticket_utils.py` — DCSync integration for KRBTGT extraction
  - `utils/reporting.py` — Ticket operation reporting
  - `utils/commands.py` — Cross-platform command reference (Impacket + Rubeus + Mimikatz)
- `16-ticket-attacks/ticket_quickref/decision_tree.py` — Operator decision flowchart: material in hand → attack type → platform-specific commands

### Changed
- Updated `README.md` to v4.0.0 with full repository structure and all 24 published article links
- Added `CHANGELOG.md` as standalone file (previously inline in README)
- Expanded Tool Categories and Usage Examples sections
- Updated badges, version, and last-updated metadata

---

## [3.0.0] — 2025-12 (Days 15–21: Lateral Movement & Privilege Escalation)

### Added — Day 15: Credential Harvesting
- Multi-method LSASS dumping (comsvcs.dll, MiniDumpWriteDump, direct memory access)
- SAM/SYSTEM hash extraction framework
- Registry credential mining (LSA secrets, AutoLogon, WiFi, cached credentials)
- DPAPI decryption (browser passwords, Windows Vault)
- Credential consolidation engine with pattern analysis and password reuse detection
- Automated harvester with intelligent method selection and evasion

### Added — Day 16: Windows Privilege Escalation
- `08-privilege-escalation/windows_privesc.py` — Automated enumeration engine
- Service misconfiguration detection (unquoted paths, weak permissions, writable binaries)
- AlwaysInstallElevated detection
- Scheduled task abuse identification
- DLL hijacking via writable PATH directories
- Token privilege analysis (SeImpersonate, SeDebug, SeBackup, etc.)
- Startup folder permission checks
- Exploitation guide generation with prioritized findings

### Added — Day 17: Linux Privilege Escalation
- `08-privilege-escalation/linux_privesc.py` — Linux enumeration framework
- SUID/GUID binary discovery and GTFOBins cross-reference
- Sudo misconfiguration detection
- Cron job analysis for writable script exploitation
- Capability enumeration
- Kernel version vs. exploit mapping
- Writable /etc/passwd and /etc/shadow detection

### Added — Day 18: Lateral Movement Techniques
- `07-lateral-movement/credential_reuse.py` — Pass-the-Hash, WMI, PSRemoting
- CrackMapExec integration for network-wide credential testing
- Impacket wmiexec, smbexec, psexec wrappers
- PSRemoting session management
- Stealth level classification per technique (LOW/MEDIUM/HIGH)

### Added — Day 19: Pivoting & Network Tunneling
- `12-network-pivoting/ssh_tunneling_framework/` — SSH tunneling framework
  - Local, remote, and dynamic (SOCKS) port forwarding
  - Tunnel lifecycle management (create, list, kill)
  - Input validation and comprehensive error handling
  - QUICKSTART.md and API documentation
- `05-persistence/rt_network_discovery/` — Network discovery for target prioritization
  - Host discovery (ping sweep, ARP)
  - Port scanning with service identification (18 common ports)
  - SMB enumeration for share discovery
  - Lateral movement target generation and prioritization

### Added — Day 20: Exploiting Trust Relationships
- `13-trust-exploitation/rt_trust_enumeration/` — Trust enumeration (PowerView, LDAP, Impacket)
  - Trust type classification (Parent-Child, Forest, External, MIT)
  - Mermaid and Graphviz trust map visualization
  - Automatic exploitability assessment per trust
- `13-trust-exploitation/rt_sid_history/` — SID history injection framework
  - Parent-child trust escalation (Domain Admin → Enterprise Admin)
  - Golden ticket with ExtraSIDs
  - Impacket raiseChild integration
- `13-trust-exploitation/rt_auto_exploit/` — Automated trust exploitation workflow

### Added — Day 21: Week 3 Integration
- `Week-3-Final/orchestrator/` — Week 3 Attack Orchestrator
  - `models/` — Credential, CompromisedSystem, AttackState data models with enums
  - `phases/privesc.py` — Phase 1: Privilege escalation
  - `phases/credential_harvest.py` — Phase 2: Credential harvesting
  - `phases/lateral_movement.py` — Phase 3: Lateral movement with stealth filtering
  - `phases/pivoting.py` — Phase 4: Network pivoting
  - `phases/trust_exploit.py` — Phase 5: Trust exploitation, DCSync, KRBTGT extraction
  - `core/orchestrator.py` — Main orchestration engine
  - `core/logger.py` — Operation logging
  - `core/reporter.py` — Report generation
  - `cli.py` — Full CLI interface with phase selection and output directory management

---

## [2.0.0] — 2025-11 (Days 8–14: Persistence & Command Control)

### Added — Day 8: Windows Persistence
- `05-persistence/windows_persistence.py` — Multi-mechanism Windows persistence
- `05-persistence/windows_persistence_tools/rt_service_persistence/` — Service persistence framework
  - 3 service creation methods (direct, C# wrapper, modify existing)
  - Detection scanning for suspicious services
  - Automatic cleanup and restore script generation
  - CLI and Python API interfaces

### Added — Day 9: Linux Persistence
- `05-persistence/linux_persistence.py` — Linux persistence mechanisms
- Cron job persistence, SSH authorized key injection
- Systemd service creation, shared object hijacking
- PAM backdoor implementation, bashrc/profile modification

### Added — Day 10: Custom C2 Infrastructure
- `06-command-control/c2_server.py` — HTTP/HTTPS-based C2 server
- `06-command-control/c2_client.py` — Multi-platform C2 client (implant)
- Encrypted communication, task queuing, beacon management

### Added — Day 11: C2 Communication Channels
- DNS tunneling C2 channel
- Cloud service C2 (Slack, Discord integration)
- Multi-channel failover and redundancy
- Domain fronting guidance

### Added — Day 12: Data Exfiltration
- `Week-2-Final/exfiltration_framework/rt_exfiltration/` — Complete exfiltration pipeline
  - `core/staging_area.py` — Data staging (raw → encrypted → chunked)
  - HTTP, DNS, ICMP exfiltration channels
  - AES encryption for data in transit
  - Secure cleanup with cryptographic file wiping

### Added — Day 13: Operational Security
- Anti-forensics techniques and automation
- Log manipulation and timestomping
- Artifact cleanup procedures
- OPSEC checklists for pre/post-operation

### Added — Day 14: Week 2 Integration
- `Week-2-Final/rt_initial_access_framework/` — Initial access automation
- `Week-2-Final/post_exploitation_framework/` — Post-exploitation suite
  - `modules/privilege_escalation.py` — PrivEsc check engine
  - `modules/sensitive_data.py` — Sensitive data discovery (credentials, configs, source code, certs, cloud sync, backups)
- `Week-2-Final/rt_lab_environment_framework/` — Lab setup automation

---

## [1.0.0] — 2025-10-25 (Days 1–7: Reconnaissance & Initial Access)

### Added — Day 1: Cyber Kill Chain
- Series introduction and methodology framework
- Kill chain phase documentation (`docs/day01-kill-chain.md`)

### Added — Day 2: OSINT & External Reconnaissance
- `01-reconnaissance/subdomain_enum.py` — DNS subdomain enumeration
- `01-reconnaissance/web_checker.py` — Web service detection
- `01-reconnaissance/google_dorker.py` — Automated Google dork queries
- `01-reconnaissance/email_hunter.py` — Email address harvesting
- `01-reconnaissance/tech_fingerprinter.py` — Technology stack identification
- `01-reconnaissance/master_recon.py` — Unified recon orchestrator
- `01-reconnaissance/wordlists/` — Subdomain and directory wordlists

### Added — Day 3: Weaponization
- `02-weaponization/payload_generator.py` — Multi-format payload generation
- `02-weaponization/advanced_obfuscator.py` — AV evasion obfuscation
- `02-weaponization/shellcode_encoder.py` — XOR/AES shellcode encoding
- `02-weaponization/macro_generator.py` — Office macro weaponization

### Added — Day 4: Social Engineering & Delivery
- `03-delivery/phishing_framework.py` — Campaign management with tracking
- `03-delivery/email_templates/` — Platform-specific phishing templates (Office 365, LinkedIn, social media)
- `03-delivery/landing_pages/` — Credential harvesting pages

### Added — Day 5: Initial Exploitation
- `04-exploitation/exploit_framework.py` — Modular exploitation engine
- Web exploitation templates (SQLi, XSS, file upload, RCE)

### Added — Day 6: Post-Exploitation
- Situational awareness scripts and initial enumeration automation
- System profiling and credential discovery

### Added — Day 7: Week 1 Integration
- `Week-1-Final/RedTeam-Framework/` — Complete Week 1 framework
  - `core/reporter.py` — Engagement report generation (markdown)
  - `templates/` — Attack chain templates (web app, domain compromise, lateral movement, exfiltration, ransomware simulation)
  - `labs/` — Docker/Vagrant practice lab management with 10+ lab definitions
  - `ctf/` — Week 1 CTF challenge with 6 flags across the full kill chain
  - `scenarios/` — Practice scenario generator with difficulty filtering and progress tracking
- Report templates (`templates/recon_report.md`, `engagement_notes.md`, `findings_template.md`, `executive_summary.md`)
- Utility scripts (`scripts/verify_setup.py`, `scripts/lab_setup.sh`, `scripts/cleanup.py`)
- Project documentation (CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE)

---

## Upcoming Releases

### [5.0.0] — Planned (Days 25–27)
- Day 25: DCSync attack framework & domain admin compromise
- Day 26: Domain-level persistence (AdminSDHolder, GPO backdoors, skeleton key, DSRM)
- Day 27: Week 4 integration orchestrator

### [6.0.0] — Planned (Days 28–30)
- Day 28: Advanced evasion & EDR bypass techniques
- Day 29: Purple team & defensive perspective
- Day 30: Series wrap-up, career guidance, complete toolkit documentation

---

*Maintained by Maxwell Cross — [Medium](https://medium.com/@maxwellcross) | [GitHub](https://github.com/itsmaxwellcross)*