#!/usr/bin/env python3
"""Reproduce the three exact mutations that escaped the v1.0.0 fixture suite."""
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MUTANTS = [
    ('disable_involution',
     'cyclic_states = [s for s in states if selected_cycle[s] is not None]',
     'cyclic_states = []  # AUDIT MUTANT: discard every cyclic state'),
    ('discard_previous_cycle_factors',
     'expanded = exponential_product(expanded, factor)',
     'expanded = exponential_product({0: ONE}, factor)  # AUDIT MUTANT: forget earlier cycles'),
    ('wrong_reversal_J_check',
     'require(delta_j in (-2, 2), "reversal J change")',
     'require(delta_j == 0, "reversal J change")  # AUDIT MUTANT: invalid requirement'),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'replay_output'/'historical-mutants')
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    results = []
    for name, before, after in MUTANTS:
        with tempfile.TemporaryDirectory(prefix='family180_historical_') as tmp:
            target = Path(tmp)
            for file in ROOT.glob('*.py'):
                shutil.copyfile(file, target/file.name)
            for directory in ('fixtures', 'certificates', 'baseline'):
                shutil.copytree(ROOT/directory, target/directory)
            code = (target/'checker.py').read_text()
            if code.count(before) != 1:
                raise RuntimeError(name + ': source replacement does not match exactly once')
            changed = code.replace(before, after)
            compile(changed, 'checker.py', 'exec')
            (target/'checker.py').write_text(changed)
            runs = []
            for label, args in [('tests', ['-m','unittest','-v','test_nonvacuous']), ('replay',['replay.py'])]:
                result = subprocess.run([sys.executable,*args], cwd=target, env=env,
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
                text = result.stdout.replace(str(target), '<temporary-workspace>')
                (output/(name+'-'+label+'.log')).write_text(text+f'\nEXIT {result.returncode}\n')
                failing = re.findall(r'^(?:FAIL|ERROR): (test_\w+)', text, re.M)
                if result.returncode == 0 or (label == 'tests' and not failing):
                    raise RuntimeError(name + ': mutation survived or failed without semantic tests')
                runs.append({'mode':label,'exit':result.returncode,'failing_tests':failing})
            results.append({'mutant':name,'replace':before,'with':after,'syntax_valid':True,
                            'status':'KILLED_BY_SEMANTIC_TESTS','runs':runs})
    (output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'historical_mutants':len(results),'killed':len(results),'results':results},sort_keys=True))

if __name__ == '__main__':
    main()
