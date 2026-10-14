#!/usr/bin/env python3
"""Execute explicitly defined implementation mutants in isolated temp copies.
These are NEW local mutants. No definitions of the three Atlas mutants were
supplied, and this script does not claim to reproduce them. Hash checks are not
part of mutant detection: the unchanged semantic unittest suite must fail.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent
MUTANTS=[
 ('M01_identity_reversal','checker.py',
  '    boundary = {edge(*d) for d in darts(cycle)}\n    q = T.q_edges(s)',
  '    return r  # injected identity operation\n    boundary = {edge(*d) for d in darts(cycle)}\n    q = T.q_edges(s)',1),
 ('M02_skip_all_cyclic_fibers','checker.py',
  '    cyclic_states = [s for s in states if selected_cycle[s] is not None]',
  '    cyclic_states = []  # injected coverage bypass',1),
 ('M03_corrupt_index_difference','checker.py',
  '            delta_j = T.index(rr, s) - T.index(r, s)',
  '            delta_j = 0  # injected corrupt index difference',1),
 ('M04_disable_entire_fiber_validator','involution.py',
  "    c.require(certificate.get('schema')=='family180-reversal-fibers-v1','fiber schema')",
  "    return {'qualifying_fibers':1,'partner_rows_checked':2,'two_element_orbits':1,'status':'PASS'}\n    c.require(certificate.get('schema')=='family180-reversal-fibers-v1','fiber schema')",1),
 ('M05_disable_phase_record_validation','involution.py',
  "            c.require(row['phase_before']==list(c.phase(before)) and row['phase_after']==list(c.phase(after)),'recorded phases recomputed')",
  '            pass  # injected phase-record validation bypass',1),
 ('M06_disable_weight_record_validation','involution.py',
  "            c.require(row['weight_before']==weight and row['weight_after']==weight,'fixed-state weight unchanged')",
  '            pass  # injected weight-record validation bypass',1),
 ('M07_disable_index_change_validation','involution.py',
  "            c.require(after-before in (-2,2) and row['J_change']==after-before,'index change plus or minus two')",
  '            pass  # injected index-change validation bypass',1),
 ('M08_disable_orbit_record_validation','involution.py',
  "        c.require(f['orbits']==[list(o) for o in orbits] and all(len(set(o))==2 for o in orbits),'complete two-element orbits')",
  '        pass  # injected orbit-record validation bypass',1),
 ('M09_disable_fixed_second_state_validation','involution.py',
  "            c.require(row['second_state_before']==list(s) and row['second_state_after']==list(s),'second state unchanged')",
  '            pass  # injected second-state validation bypass',1),
 ('M10_ignore_claimed_cancellation_sum','involution.py',
  "        c.require(total=={} and f['fixed_state_exponential_sum']==c.serialize_exp(total),'exact fixed-state cancellation')",
  "        c.require(total=={},'exact fixed-state cancellation')  # injected record bypass",1),
 ('M11_truncate_cycle_decomposition','checker.py',
  '        cycles = cycle_union(T.X, D)',
  '        cycles = cycle_union(T.X, D)[:1]  # injected omitted cycles',2),
 ('M12_omit_reverse_orientations','checker.py',
  '        for flips in product((False, True), repeat=len(cycles)):',
  '        for flips in product((False,), repeat=len(cycles)):  # injected missing orientations',1),
]


def run_case(name,mutation=None,output=None):
    output=ROOT if output is None else output
    env=dict(os.environ);env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='family180_mutant_') as tmp:
        td=Path(tmp)
        for file in ROOT.glob('*.py'):shutil.copyfile(file,td/file.name)
        for folder in ('fixtures','certificates','baseline'):shutil.copytree(ROOT/folder,td/folder)
        info={'id':name,'unchanged_test_file_sha256':hashlib.sha256((td/'test_nonvacuous.py').read_bytes()).hexdigest()}
        if mutation:
            _,filename,old,new,count=mutation
            source=(td/filename).read_text()
            if source.count(old)!=count:raise RuntimeError(f'{name}: expected {count} source matches, got {source.count(old)}')
            changed=source.replace(old,new);compile(changed,str(td/filename),'exec')
            (td/filename).write_text(changed)
            diff=''.join(difflib.unified_diff(source.splitlines(True),changed.splitlines(True),fromfile=filename,tofile=name+'/'+filename))
            (output/'mutations'/f'{name}.patch').write_text(diff)
            info.update({'file':filename,'source_matches':count,'syntax_valid':True,
                         'unmutated_sha256':hashlib.sha256(source.encode()).hexdigest(),
                         'mutated_sha256':hashlib.sha256(changed.encode()).hexdigest()})
        cmd=[sys.executable,'-m','unittest','-v','test_nonvacuous']
        p=subprocess.run(cmd,cwd=td,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
        text=p.stdout
        (output/'logs'/'mutations'/f'{name}.log').write_text('COMMAND: python3 -m unittest -v test_nonvacuous\n'+text)
        info.update({'returncode':p.returncode,'elapsed_seconds':time.monotonic()-start,
                     'detected_by_tests':sorted(set(re.findall(r'^(?:FAIL|ERROR): (test_\w+)',text,re.M))),
                     'test_summary':re.findall(r'^(?:Ran \d+ tests.*|OK|FAILED.*)$',text,re.M)})
        if mutation:
            if p.returncode==0:raise RuntimeError(f'{name}: SURVIVED; do not report as detected')
            if not info['detected_by_tests']:raise RuntimeError(f'{name}: infrastructure error, not a test kill')
            info['status']='KILLED_BY_SEMANTIC_TESTS'
        else:
            if p.returncode:raise RuntimeError('unmutated control failed')
            info['status']='CONTROL_PASS'
        return info


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'replay_output'/'mutation_replay',help='new replay records; delivered records are not overwritten by default')
    output=parser.parse_args().output.resolve()
    (output/'mutations').mkdir(parents=True,exist_ok=True);(output/'logs'/'mutations').mkdir(parents=True,exist_ok=True)
    definitions=[{'id':n,'file':f,'replace':a,'with':b,'expected_matches':k} for n,f,a,b,k in MUTANTS]
    (output/'mutations'/'definitions.json').write_text(json.dumps({'atlas_mutants_reproduced':False,'reason':'definitions not supplied','mutants':definitions},indent=2)+'\n')
    results=[run_case('control',output=output)]
    print(json.dumps(results[0],sort_keys=True),flush=True)
    for m in MUTANTS:
        r=run_case(m[0],m,output=output);results.append(r);print(json.dumps(r,sort_keys=True),flush=True)
    summary={'unmutated_control':'PASS','defined_mutants':len(MUTANTS),'killed':len(results)-1,'survived':0,'atlas_mutants_reproduced':False,'results':results}
    (output/'mutation_results.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
