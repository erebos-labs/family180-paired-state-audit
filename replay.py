#!/usr/bin/env python3
"""Read-only replay of primary, orbit and independent exact checks."""
import json
from pathlib import Path
import checker
import involution
import independent_check

ROOT=Path(__file__).resolve().parent

def main():
    paths=list((ROOT/'fixtures').glob('*.json'))
    checker.require(len(paths)==1,'only the one declared follow-up fixture')
    f=json.loads(paths[0].read_text())
    a=json.loads((ROOT/'certificates'/f"{f['name']}.json").read_text())
    b=json.loads((ROOT/'certificates'/'reversal_fibers.json').read_text())
    checker.verify_certificate(f,a)
    orbit=involution.verify_certificate(f,b)
    review=independent_check.verify(f,a,b)
    stored=json.loads((ROOT/'certificates'/'independent_report.json').read_text())
    checker.require(review==stored,'independent report differs on replay')
    print(json.dumps({'primary':a['summary'],'orbit_validation':orbit,'independent':review},indent=2,sort_keys=True))

if __name__=='__main__':main()
