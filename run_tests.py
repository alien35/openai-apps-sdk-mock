#!/usr/bin/env python3
"""Master test runner for insurance server unit tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --coverage         # With coverage report
    python run_tests.py --fast             # Skip slow tests
    python run_tests.py --phone-only       # Run only phone-only state tests
    python run_tests.py --smoke            # Run only smoke tests (quick)
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print_info(f"{description}...")
    print(f"{Colors.BOLD}Command: {' '.join(cmd)}{Colors.ENDC}\n")

    try:
        result = subprocess.run(cmd, check=True, text=True)
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        print_info("Make sure pytest is installed: pip install pytest pytest-asyncio pytest-cov")
        return False


def check_environment():
    """Check that required packages are installed."""
    print_header("Checking Test Environment")

    # Use sys.executable to ensure we're checking the same Python that's running this script
    python_exe = sys.executable

    required = [
        ("pytest", [python_exe, "-m", "pytest", "--version"]),
        ("pytest-asyncio", [python_exe, "-c", "import pytest_asyncio; print(pytest_asyncio.__version__)"]),
        ("pytest-cov", [python_exe, "-c", "import pytest_cov; print(pytest_cov.__version__)"]),
    ]

    all_installed = True
    for package, check_cmd in required:
        try:
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"{package} is installed: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error(f"{package} is NOT installed")
            all_installed = False

    if not all_installed:
        print_info("\nInstall missing packages:")
        print(f"{Colors.BOLD}  pip install pytest pytest-asyncio pytest-cov{Colors.ENDC}\n")
        return False

    return True


def run_phone_only_tests(verbose: bool = False, coverage: bool = False) -> bool:
    """Run phone-only state tests."""
    print_header("Running Phone-Only State Tests")

    cmd = [sys.executable, "-m", "pytest", "insurance_server_python/tests/test_phone_only_states.py"]

    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    if coverage:
        cmd.extend([
            "--cov=insurance_server_python.carrier_mapping",
            "--cov=insurance_server_python.utils",
            "--cov=insurance_server_python.tool_handlers",
            "--cov-report=term-missing",
        ])

    cmd.append("--tb=short")

    return run_command(cmd, "Phone-only state tests")


def run_smoke_tests(verbose: bool = False) -> bool:
    """Run quick smoke tests."""
    print_header("Running Smoke Tests")

    cmd = [
        sys.executable, "-m", "pytest",
        "insurance_server_python/tests/test_phone_only_states.py::TestIntegrationSmokeTests",
        "-v" if not verbose else "-vv",
        "--tb=short"
    ]

    return run_command(cmd, "Smoke tests")


def run_all_tests(verbose: bool = False, coverage: bool = False, fast: bool = False) -> bool:
    """Run all tests in the test suite."""
    print_header("Running All Unit Tests")

    cmd = [sys.executable, "-m", "pytest", "insurance_server_python/tests/"]

    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    if fast:
        cmd.append("-m")
        cmd.append("not slow")

    if coverage:
        cmd.extend([
            "--cov=insurance_server_python",
            "--cov-report=html",
            "--cov-report=term-missing",
        ])

    cmd.append("--tb=short")

    success = run_command(cmd, "All tests")

    if success and coverage:
        print_info("\nCoverage report generated: htmlcov/index.html")
        print(f"{Colors.BOLD}  open htmlcov/index.html{Colors.ENDC}\n")

    return success


def print_test_summary(results: dict):
    """Print a summary of test results."""
    print_header("Test Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"Total test suites: {total}")
    print(f"Passed: {Colors.OKGREEN}{passed}{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{failed}{Colors.ENDC}")

    print("\nResults by suite:")
    for suite, success in results.items():
        status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if success else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        print(f"  {suite}: {status}")

    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some tests failed{Colors.ENDC}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run insurance server unit tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --verbose          # Verbose output
  python run_tests.py --coverage         # With coverage report
  python run_tests.py --phone-only       # Only phone-only state tests
  python run_tests.py --smoke            # Quick smoke tests (< 5s)
  python run_tests.py --fast --coverage  # Fast tests with coverage
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )

    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="Skip slow tests"
    )

    parser.add_argument(
        "--phone-only", "-p",
        action="store_true",
        help="Run only phone-only state tests"
    )

    parser.add_argument(
        "--smoke", "-s",
        action="store_true",
        help="Run only smoke tests (quick)"
    )

    parser.add_argument(
        "--no-env-check",
        action="store_true",
        help="Skip environment check"
    )

    args = parser.parse_args()

    # Print banner
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                   Insurance Server - Unit Test Runner                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    # Check environment
    if not args.no_env_check:
        if not check_environment():
            return 1

    # Run tests based on arguments
    results = {}

    if args.smoke:
        # Quick smoke tests only
        results["Smoke Tests"] = run_smoke_tests(args.verbose)

    elif args.phone_only:
        # Phone-only state tests only
        results["Phone-Only State Tests"] = run_phone_only_tests(args.verbose, args.coverage)

    else:
        # Run all tests
        results["All Tests"] = run_all_tests(args.verbose, args.coverage, args.fast)

    # Print summary
    exit_code = print_test_summary(results)

    print(f"\n{Colors.BOLD}Test run completed.{Colors.ENDC}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
