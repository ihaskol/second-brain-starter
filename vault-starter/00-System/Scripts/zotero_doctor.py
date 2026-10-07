#!/usr/bin/env python3
"""
Zotero Integration Health Check
Second Brain - Academic Source Management

Verifies Zotero connectivity and Second Brain readiness.

Usage:
    python3 zotero_doctor.py [--vault-root PATH]

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
    2 - Critical error (invalid arguments, missing dependencies)
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed")
    print("Install: pip3 install requests")
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML library not installed")
    print("Install: pip3 install pyyaml")
    sys.exit(2)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {text} ==={Colors.RESET}")


def print_pass(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_fail(text: str):
    """Print failure message"""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_warn(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"  {text}")


def check_vault_root(vault_root: Path) -> bool:
    """Check if vault root exists and contains expected structure"""
    print_header("Vault Structure")

    if not vault_root.exists():
        print_fail(f"Vault root not found: {vault_root}")
        return False
    print_pass(f"Vault root exists: {vault_root}")

    # Check critical directories
    critical_dirs = [
        "00-System",
        "00-System/Scripts",
        "00-System/Config",
        "01-Library/Originals",
        "01-Library/Reports",
        "02-Wiki",
        "05-Inbox",
    ]

    all_exist = True
    for dir_path in critical_dirs:
        full_path = vault_root / dir_path
        if full_path.exists():
            print_pass(f"{dir_path}/ exists")
        else:
            print_fail(f"{dir_path}/ NOT FOUND")
            all_exist = False

    return all_exist


def check_zotero_api(config: Dict) -> Tuple[bool, Dict]:
    """Check Zotero local API connectivity"""
    print_header("Zotero Local API")

    base_url = config['local_api']['base_url']
    timeout = config['local_api']['timeout_seconds']
    library_type = config['local_api']['library_type']

    # Test collections endpoint directly (root endpoint may not exist)
    try:
        collections_url = f"{base_url}/users/0/collections"
        response = requests.get(collections_url, timeout=timeout)

        if response.status_code == 200:
            collections = response.json()
            print_pass("Local API is enabled and reachable")
            print_pass(f"Collections accessible ({len(collections)} collections)")

            # Extract library ID from first collection
            library_info = {}
            if collections:
                first_coll = collections[0]
                library_info = {
                    'library_id': first_coll['library']['id'],
                    'library_name': first_coll['library']['name'],
                    'library_type': first_coll['library']['type']
                }
                print_info(f"Library: {library_info['library_name']} (ID: {library_info['library_id']})")

            return True, library_info
        else:
            print_fail(f"Collections endpoint returned status {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False, {}

    except requests.exceptions.ConnectionError:
        print_fail("Cannot connect to Zotero local API")
        print_info("Ensure Zotero desktop is running")
        print_info("Check: Preferences → Advanced → 'Allow other applications to communicate'")
        return False, {}
    except Exception as e:
        print_fail(f"API connection error: {e}")
        return False, {}


def check_config_file(vault_root: Path) -> Tuple[bool, Dict]:
    """Check Zotero integration config file"""
    print_header("Configuration")

    config_path = vault_root / "00-System/Config/zotero-integration.yml"

    if not config_path.exists():
        print_fail(f"Config file not found: {config_path}")
        return False, {}

    print_pass(f"Config file exists: {config_path.name}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print_pass("Config file valid YAML")

        # Verify required fields
        required_fields = [
            ('integration_mode', str),
            ('local_api', dict),
            ('duplicate_checks', list),
        ]

        for field, expected_type in required_fields:
            if field in config and isinstance(config[field], expected_type):
                print_pass(f"Field '{field}' present and valid")
            else:
                print_fail(f"Field '{field}' missing or invalid type")
                return False, {}

        return True, config

    except yaml.YAMLError as e:
        print_fail(f"Invalid YAML: {e}")
        return False, {}
    except Exception as e:
        print_fail(f"Config read error: {e}")
        return False, {}


def check_scripts(vault_root: Path) -> bool:
    """Check that required Python scripts exist and compile"""
    print_header("Pipeline Scripts")

    scripts_dir = vault_root / "00-System/Scripts"

    required_scripts = [
        "inspect-pdf.py",
        "process-source.py",
        "validate-text.py",
        "add-page-markers.py",
        "zotero_search.py",
        "zotero_import.py",
    ]

    all_exist = True
    for script_name in required_scripts:
        script_path = scripts_dir / script_name
        if not script_path.exists():
            print_fail(f"{script_name} NOT FOUND")
            all_exist = False
            continue

        # Try to compile
        try:
            subprocess.run(
                ["python3", "-m", "py_compile", str(script_path)],
                check=True,
                capture_output=True,
                timeout=5
            )
            print_pass(f"{script_name} exists and compiles")
        except subprocess.CalledProcessError as e:
            print_fail(f"{script_name} syntax error: {e.stderr.decode()[:100]}")
            all_exist = False
        except Exception as e:
            print_warn(f"{script_name} compile check failed: {e}")

    return all_exist


def check_process_sources_skill(vault_root: Path) -> bool:
    """Check if /process-sources skill exists"""
    print_header("Process Sources Integration")

    skill_path = vault_root / ".claude/skills/process-sources/SKILL.md"

    if not skill_path.exists():
        print_fail("/process-sources skill NOT FOUND")
        print_info("Zotero integration requires /process-sources for PDF processing")
        return False

    print_pass("/process-sources skill exists")
    return True


def check_inbox_writable(vault_root: Path) -> bool:
    """Check if 05-Inbox is writable"""
    print_header("Inbox Writability")

    inbox_dir = vault_root / "05-Inbox"

    if not inbox_dir.exists():
        print_fail("05-Inbox directory does not exist")
        return False

    # Try to create and delete a test file
    test_file = inbox_dir / ".zotero_doctor_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print_pass("05-Inbox is writable")
        return True
    except Exception as e:
        print_fail(f"05-Inbox not writable: {e}")
        return False


def check_credentials_safety(vault_root: Path) -> bool:
    """Check that no credentials are stored in Git-tracked files"""
    print_header("Credential Safety")

    # Check if we're in a Git repo
    git_dir = vault_root / ".git"
    if not git_dir.exists():
        print_warn("Not a Git repository (safety check skipped)")
        return True

    # Check config file for API keys
    config_path = vault_root / "00-System/Config/zotero-integration.yml"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()

        # Look for suspicious patterns
        suspicious_patterns = [
            "api_key:",
            "password:",
            "secret:",
            "token:",
            "ZOTERO_API_KEY",
        ]

        found_suspicious = []
        for pattern in suspicious_patterns:
            if pattern in config_content:
                found_suspicious.append(pattern)

        if found_suspicious:
            print_fail(f"Found credential patterns: {', '.join(found_suspicious)}")
            print_warn("Ensure no actual credentials are committed to Git")
            return False
        else:
            print_pass("No credential patterns found in config")
            return True

    except Exception as e:
        print_warn(f"Could not check credentials: {e}")
        return True


def check_python_dependencies() -> bool:
    """Check that required Python libraries are installed"""
    print_header("Python Dependencies")

    required = [
        ('requests', 'pip3 install requests'),
        ('yaml', 'pip3 install pyyaml'),
        ('pypdf', 'pip3 install pypdf'),
        ('pytesseract', 'pip3 install pytesseract'),
    ]

    all_present = True
    for module_name, install_cmd in required:
        try:
            __import__(module_name)
            print_pass(f"{module_name} installed")
        except ImportError:
            print_fail(f"{module_name} NOT INSTALLED")
            print_info(f"Install: {install_cmd}")
            all_present = False

    return all_present


def main():
    parser = argparse.ArgumentParser(
        description="Zotero integration health check for Second Brain"
    )
    parser.add_argument(
        '--vault-root',
        type=Path,
        help="Path to Second Brain vault root (default: current directory)"
    )

    args = parser.parse_args()
    vault_root = args.vault_root or Path.cwd()

    print(f"{Colors.BOLD}Zotero Integration Health Check{Colors.RESET}")
    print(f"Vault: {vault_root}")

    # Run all checks
    checks = []

    # 1. Vault structure
    checks.append(("Vault Structure", check_vault_root(vault_root)))

    # 2. Configuration
    config_ok, config = check_config_file(vault_root)
    checks.append(("Configuration", config_ok))

    # 3. Zotero API (only if config loaded)
    if config_ok:
        api_ok, library_info = check_zotero_api(config)
        checks.append(("Zotero API", api_ok))

        # Update config with detected library ID
        if library_info and 'library_id' in library_info:
            detected_id = library_info['library_id']
            config_id = config['local_api'].get('library_id')
            if config_id != detected_id:
                print_warn(f"Config library_id ({config_id}) != detected ({detected_id})")
                print_info("Consider updating 00-System/Config/zotero-integration.yml")
    else:
        checks.append(("Zotero API", False))

    # 4. Scripts
    checks.append(("Pipeline Scripts", check_scripts(vault_root)))

    # 5. Process Sources skill
    checks.append(("Process Sources", check_process_sources_skill(vault_root)))

    # 6. Inbox writable
    checks.append(("Inbox Writable", check_inbox_writable(vault_root)))

    # 7. Credential safety
    checks.append(("Credential Safety", check_credentials_safety(vault_root)))

    # 8. Python dependencies
    checks.append(("Python Dependencies", check_python_dependencies()))

    # Summary
    print_header("Summary")

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{status} - {check_name}")

    print()
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed ({passed}/{total}){Colors.RESET}")
        print(f"\nZotero integration is ready to use.")
        print(f"Try: /zotero-sources collections")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ {total - passed} check(s) failed ({passed}/{total}){Colors.RESET}")
        print(f"\nResolve failures above before using /zotero-sources.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
