"""
run_all_tests.py — Jalankan semua test MIRU Backend API.

Usage:
    python run_all_tests.py                  # Verbose output
    python run_all_tests.py --parallel       # Parallel (lebih cepat)
    python run_all_tests.py --failfast       # Berhenti di failure pertama

Note:
    Cukup 'python manage.py test api.tests --verbosity=1' juga bisa.
"""

import os
import subprocess
import sys

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    args = [sys.executable, 'manage.py', 'test', 'api.tests', '--verbosity=1']
    if '--parallel' in sys.argv:
        args.append('--parallel')
    if '--failfast' in sys.argv:
        args.append('--failfast')

    env = os.environ.copy()
    env['USE_POSTGRES'] = 'False'

    print(f"Running: {' '.join(args)}")
    result = subprocess.run(args, env=env)
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
