#!/usr/bin/env python3
"""
================================================================================
30 Days of Red Team - Import Verification Test
================================================================================

Tests imports across all phases of the toolkit to verify migration success.
Run from the repository root.

Usage:
    python test_imports.py

================================================================================
"""

import sys
from pathlib import Path

# Get repo root (assuming script is in repo root or tools/)
SCRIPT_DIR = Path(__file__).parent.resolve()
if SCRIPT_DIR.name == 'tools':
    REPO_ROOT = SCRIPT_DIR.parent
else:
    REPO_ROOT = SCRIPT_DIR

# Define all tests: (phase_directory, import_statement, label)
TESTS = [
    # 01-reconnaissance
    ("01-reconnaissance", "from rt_tech_fingerprinter.core import fingerprinter", "tech_fingerprinter"),
    ("01-reconnaissance", "from rt_tech_fingerprinter.analyzers import header_analyzer",
     "tech_fingerprinter.analyzers"),

    # 02-weaponization
    ("02-weaponization", "from rt_payload_generator.generators import powershell", "payload_generator"),
    ("02-weaponization", "from rt_payload_generator.generators import bash", "payload_generator.bash"),
    ("02-weaponization", "from rt_macro_generator.generators import download_execute", "macro_generator"),
    ("02-weaponization", "from rt_macro_generator.evasion import sandbox_checks", "macro_generator.evasion"),
    ("02-weaponization", "from rt_shellcode_encoder.encoders import xor_encoder", "shellcode_encoder"),
    ("02-weaponization", "from rt_advanced_obfuscator.core import encoder", "advanced_obfuscator"),

    # 03-delivery
    ("03-delivery", "from rt_phishing_framework.core import campaign", "phishing_framework"),
    ("03-delivery", "from rt_phishing_framework.core import database", "phishing_framework.database"),
    ("03-delivery", "from rt_phishing_framework.tracking import tracker", "phishing_framework.tracking"),
    ("03-delivery", "from rt_template_generator.core import generator", "template_generator"),
    ("03-delivery", "from rt_template_generator.templates import it", "template_generator.templates"),
    ("03-delivery", "from rt_attachment_weaponizer.core import weaponizer", "attachment_weaponizer"),
    ("03-delivery", "from rt_attachment_weaponizer.creators import lnk_creator", "attachment_weaponizer.creators"),
    ("03-delivery", "from rt_domain_reputation.checkers import dns_checker", "domain_reputation"),

    # 04-exploitation
    ("04-exploitation", "from rt_vulnerability_scanner.checks import sql_injection", "vulnerability_scanner"),
    ("04-exploitation", "from rt_vulnerability_scanner.checks import xss", "vulnerability_scanner.xss"),
    ("04-exploitation", "from rt_vulnerability_scanner.reporting import report_generator",
     "vulnerability_scanner.reporting"),
    ("04-exploitation", "from rt_reverse_shell_handler.shell import listener", "reverse_shell_handler"),
    ("04-exploitation", "from rt_reverse_shell_handler.payloads import bash_payloads",
     "reverse_shell_handler.payloads"),
    ("04-exploitation", "from rt_service_exploiter.exploits import smb_exploit", "service_exploiter"),
    ("04-exploitation", "from rt_webshell_uploader.shells import php_shells", "webshell_uploader"),
    ("04-exploitation", "from rt_webshell_uploader.bypass import content_type", "webshell_uploader.bypass"),

    # 05-persistence
    ("05-persistence", "from rt_credential_harvester.harvesters import browser", "credential_harvester"),
    ("05-persistence", "from rt_credential_harvester.harvesters import ssh", "credential_harvester.ssh"),
    ("05-persistence", "from rt_credential_harvester.core import base", "credential_harvester.core"),
    ("05-persistence", "from rt_network_discovery.scanners import port_scanner", "network_discovery"),
    ("05-persistence", "from rt_network_discovery.scanners import host_discovery", "network_discovery.host"),
    ("05-persistence", "from rt_network_discovery.enumeration import smb", "network_discovery.enumeration"),
    ("05-persistence", "from rt_shell_stabilizer.techniques import linux_techniques", "shell_stabilizer"),
    ("05-persistence", "from rt_shell_stabilizer.techniques import windows_techniques", "shell_stabilizer.windows"),
    ("05-persistence", "from rt_situational_awareness.modules import system", "situational_awareness"),
    ("05-persistence", "from rt_situational_awareness.modules import network", "situational_awareness.network"),
    ("05-persistence", "from rt_data_exfiltrator.discovery import file_finder", "data_exfiltrator"),

    # 05-persistence (Linux persistence tools)
    ("05-persistence/linux_persistence_tools", "from rt_cron_persistence import core", "cron_persistence"),
    ("05-persistence/linux_persistence_tools", "from rt_ssh_persistence import core", "ssh_persistence"),
    ("05-persistence/linux_persistence_tools", "from rt_systemd_persistence import core", "systemd_persistence"),
    ("05-persistence/linux_persistence_tools", "from rt_shell_persistence import core", "shell_persistence"),

    # 05-persistence (Windows persistence tools)
    ("05-persistence/windows_persistence_tools", "from rt_registry_persistence.methods import run_keys",
     "registry_persistence"),
    ("05-persistence/windows_persistence_tools", "from rt_scheduled_task_persistence.triggers import logon",
     "scheduled_task_persistence"),
    ("05-persistence/windows_persistence_tools", "from rt_service_persistence.methods import create",
     "service_persistence"),
    ("05-persistence/windows_persistence_tools", "from rt_wmi_persistence.methods import logon", "wmi_persistence"),

    # 06-c2-infrastructure
    ("06-c2-infrastructure/01-c2-server", "from rt_c2_server import server", "c2_server"),
    ("06-c2-infrastructure/01-c2-server", "from rt_c2_server import database", "c2_server.database"),
    ("06-c2-infrastructure/01-c2-server", "from rt_c2_server import encryption", "c2_server.encryption"),
    ("06-c2-infrastructure/02-agents/cross-platform/python", "from rt_c2_agent import core", "c2_agent"),
    ("06-c2-infrastructure/02-agents/cross-platform/python", "from rt_c2_agent import communication",
     "c2_agent.communication"),
    ("06-c2-infrastructure/03-payload-generator", "from rt_c2_payload_generator import generator",
     "c2_payload_generator"),

    # 07-data-exfiltration
    ("07-data-exfiltration", "from rt_dns_exfil import encoder", "dns_exfil"),
    ("07-data-exfiltration", "from rt_dns_exfil import transmitter", "dns_exfil.transmitter"),
    ("07-data-exfiltration", "from rt_cloud_exfil import aws_s3", "cloud_exfil"),
    ("07-data-exfiltration", "from rt_cloud_exfil import dropbox", "cloud_exfil.dropbox"),
    ("07-data-exfiltration", "from rt_steganography import encoder", "steganography"),
    ("07-data-exfiltration", "from rt_steganography import decoder", "steganography.decoder"),
    ("07-data-exfiltration", "from rt_chunked_exfil import core", "chunked_exfil"),
    ("07-data-exfiltration", "from rt_automated_collection import collector", "automated_collection"),
    ("07-data-exfiltration", "from rt_encrypted_archive_builder.encryption import encryptor",
     "encrypted_archive_builder"),
    ("07-data-exfiltration", "from rt_bandwidth_throttling_manager.throttling import throttle", "bandwidth_throttling"),

    # 08-opsec-anti-forensics
    ("08-opsec-anti-forensics", "from rt_timestamp_stomper.core import timestamp_stomper", "timestamp_stomper"),
    ("08-opsec-anti-forensics", "from rt_timestamp_stomper.platforms import unix_handler", "timestamp_stomper.unix"),
    ("08-opsec-anti-forensics", "from rt_secure_delete.core import secure_delete", "secure_delete"),
    ("08-opsec-anti-forensics", "from rt_secure_delete.methods import overwrite_methods", "secure_delete.methods"),
    ("08-opsec-anti-forensics", "from rt_memory_executor.core import memory_executor", "memory_executor"),
    ("08-opsec-anti-forensics", "from rt_memory_executor.techniques import shellcode_injection",
     "memory_executor.shellcode"),
    ("08-opsec-anti-forensics", "from rt_linux_log_cleanup.cleaners import text_log_cleaner", "linux_log_cleanup"),
    ("08-opsec-anti-forensics", "from rt_windows_log_manipulation.generators import cleaner",
     "windows_log_manipulation"),

    # 09-credential-harvesting
    ("09-credential-harvesting/rt_dpapi_decryptor_framework", "from rt_dpapi_decryptor.decryptors import chrome",
     "dpapi_decryptor.chrome"),
    ("09-credential-harvesting/rt_dpapi_decryptor_framework", "from rt_dpapi_decryptor.decryptors import edge",
     "dpapi_decryptor.edge"),
    ("09-credential-harvesting/rt_dpapi_decryptor_framework", "from rt_dpapi_decryptor.utils import dpapi",
     "dpapi_decryptor.utils"),
    ("09-credential-harvesting/rt_lsass_dumper_framework", "from rt_lsass_dumper.methods import comsvcs",
     "lsass_dumper"),
    ("09-credential-harvesting/rt_lsass_dumper_framework", "from rt_lsass_dumper.methods import procdump",
     "lsass_dumper.procdump"),
    ("09-credential-harvesting/rt_sam_extractor_framework", "from rt_sam_extractor.methods import reg_save",
     "sam_extractor"),
    ("09-credential-harvesting/rt_sam_extractor_framework", "from rt_sam_extractor.methods import vss",
     "sam_extractor.vss"),
    ("09-credential-harvesting/rt_registry_miner_framework", "from rt_registry_miner.miners import autologon",
     "registry_miner"),
    ("09-credential-harvesting/rt_registry_miner_framework", "from rt_registry_miner.miners import wifi",
     "registry_miner.wifi"),

    # 10-privilege-escalation
    ("10-privilege-escalation", "from rt_win_privesc.modules import privileges", "win_privesc"),
    ("10-privilege-escalation", "from rt_win_privesc.core import enumerator", "win_privesc.enumerator"),
]


def run_tests():
    """Run all import tests."""
    passed = 0
    failed = 0
    failed_tests = []

    print("\n" + "=" * 70)
    print("   30 DAYS OF RED TEAM - IMPORT VERIFICATION")
    print("=" * 70)
    print(f"\n   Repository: {REPO_ROOT}\n")
    print("-" * 70)

    current_phase = None

    for phase_dir, import_stmt, label in TESTS:
        # Print phase header
        phase = phase_dir.split('/')[0]
        if phase != current_phase:
            current_phase = phase
            print(f"\n   [{phase}]")

        # Add phase directory to sys.path temporarily
        phase_path = REPO_ROOT / phase_dir

        if not phase_path.exists():
            print(f"     ⚠️  {label}: Directory not found ({phase_dir})")
            failed += 1
            failed_tests.append((phase_dir, import_stmt, label, "Directory not found"))
            continue

        # Add to path
        sys.path.insert(0, str(phase_path))

        try:
            exec(import_stmt)
            print(f"     ✅ {label}")
            passed += 1
        except Exception as e:
            print(f"     ❌ {label}")
            print(f"        └─ {type(e).__name__}: {e}")
            failed += 1
            failed_tests.append((phase_dir, import_stmt, label, str(e)))
        finally:
            # Remove from path
            sys.path.remove(str(phase_path))

    # Summary
    print("\n" + "=" * 70)
    print(f"   RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed_tests:
        print("\n   FAILED TESTS:")
        print("-" * 70)
        for phase_dir, import_stmt, label, error in failed_tests[:10]:
            print(f"\n   [{phase_dir}] {label}")
            print(f"   Import: {import_stmt}")
            print(f"   Error:  {error}")

        if len(failed_tests) > 10:
            print(f"\n   ... and {len(failed_tests) - 10} more failures")

    print("\n")
    return failed == 0


def main():
    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()