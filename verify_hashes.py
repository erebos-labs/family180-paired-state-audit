#!/usr/bin/env python3
"""Verify SHA-256 of delivered files. This does not replace semantic replay."""
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    count=0
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        path=Path(name)
        if path.is_absolute() or '..' in path.parts:raise ValueError('unsafe manifest path')
        data=(ROOT/path).read_bytes()
        if sha256(data).hexdigest()!=digest:raise ValueError('SHA256 mismatch: '+name)
        count+=1
    print(f'PASS: {count} delivered file hashes verified; run replay.py for semantic validation.')

if __name__=='__main__':main()
