#!/usr/bin/env python3
"""Replay the byte-preserved public v1.0.0 source/data subset."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    work = ROOT / 'baseline' / 'v1.0.0'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    for args in [('verify_hashes.py',), ('checker.py',), ('-m', 'unittest', '-v', 'test_checker')]:
        print('COMMAND: python3 ' + ' '.join(args), flush=True)
        subprocess.run([sys.executable, *args], cwd=work, env=env, check=True, timeout=45)
    print('PASS: public baseline source/data hashes, four fixtures, 27 tests')

if __name__ == '__main__':
    main()
