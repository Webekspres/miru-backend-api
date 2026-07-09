"""
run_all_tests.py — Full test suite runner for MIRU Backend API.

Usage:
    python run_all_tests.py                        # Run all tests
    python run_all_tests.py --verbose               # Verbose output
    python run_all_tests.py --failfast             # Stop on first failure
    python run_all_tests.py --coverage             # Show coverage report (requires coverage.py)

Exits with 0 if all tests pass, 1 otherwise.
"""

import os
import subprocess
import sys
import time

TESTS = [
    # Authentication & Users
    'api.tests.test_health',
    'api.tests.test_auth',
    'api.tests.test_users',
    # Master Data
    'api.tests.test_waste_categories',
    'api.tests.test_price_history',
    'api.tests.test_rewards',
    'api.tests.test_seed_data',
    # Core Transactions
    'api.tests.test_deposits',
    'api.tests.test_pickups',
    'api.tests.test_withdrawals',
    'api.tests.test_redemptions',
    'api.tests.test_partner_sales',
    'api.tests.test_complaints',
    # Monitoring & Reports
    'api.tests.test_dashboard',
    'api.tests.test_reports',
    'api.tests.test_inventory',
    'api.tests.test_activity',
    # Governance
    'api.tests.test_audit_log',
    'api.tests.test_settings',
    # Integrity & Permissions
    'api.tests.test_transaction_integrity',
    'api.tests.test_role_permissions',
]

PASSED = []
FAILED = []
ERRORS = []


def print_header(text: str):
    width = 72
    print()
    print('=' * width)
    print(f'  {text}')
    print('=' * width)


def run_test(test_path: str, verbose: bool) -> bool:
    cmd = [
        sys.executable, 'manage.py', 'test', test_path,
        '--verbosity', '2' if verbose else '1',
        '--noinput',
    ]
    env = os.environ.copy()
    env['USE_POSTGRES'] = 'False'

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    elapsed = time.time() - start

    passed = result.returncode == 0
    status = 'PASS' if passed else 'FAIL'
    marker = '+' if passed else 'X'
    print(f'  [{elapsed:6.1f}s] [{marker}] {status:4s}  {test_path}')

    if not passed and verbose:
        print()
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])

    return passed


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    failfast = '--failfast' in sys.argv or '-f' in sys.argv
    do_coverage = '--coverage' in sys.argv or '-c' in sys.argv

    print_header('MIRU Bank Sampah — Full Test Suite')
    print(f'  Tests:   {len(TESTS)} modules')
    print(f'  Python:  {sys.executable}')
    print(f'  Django:  {os.path.exists("manage.py")}')
    print(f'  Verbose: {verbose}')
    print(f'  Coverage:{do_coverage}')

    if do_coverage:
        print()
        print('  Installing coverage.py if needed...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'coverage', '-q'],
            capture_output=True,
        )

    if do_coverage:
        cmd = [
            sys.executable, '-m', 'coverage', 'run',
            '--source=api',
            'manage.py', 'test',
        ] + TESTS + ['--verbosity', '1', '--noinput', '--parallel']
        if failfast:
            cmd.append('--failfast')
        env = os.environ.copy()
        env['USE_POSTGRES'] = 'False'

        print()
        print('  Running with coverage...')
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print(result.stdout[-1000:])

        subprocess.run([sys.executable, '-m', 'coverage', 'report'])
        subprocess.run([sys.executable, '-m', 'coverage', 'html'])
        print('  Coverage report: htmlcov/index.html')
    else:
        total_start = time.time()
        for test in TESTS:
            if failfast and FAILED:
                break
            ok = run_test(test, verbose)
            if ok:
                PASSED.append(test)
            else:
                FAILED.append(test)

        total_elapsed = time.time() - total_start

        print_header('Results')
        print(f'  Total:  {len(PASSED) + len(FAILED)} modules')
        print(f'  Passed: {len(PASSED)}')
        print(f'  Failed: {len(FAILED)}')
        print(f'  Time:   {total_elapsed:.1f}s')

        if FAILED:
            print()
            print('  Failed modules:')
            for f in FAILED:
                print(f'    [X] {f}')

    return 1 if FAILED else 0


if __name__ == '__main__':
    sys.exit(main())
