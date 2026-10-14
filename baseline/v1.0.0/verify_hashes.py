#!/usr/bin/env python3
"""Validate the delivered SHA-256 manifest; semantic replay is a separate step."""
from hashlib import sha256
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    entries = (root / "SHA256SUMS").read_text().splitlines()
    for line in entries:
        expected, relative = line.split("  ", 1)
        path = (root / relative).resolve()
        if root not in path.parents:
            raise SystemExit(f"Invalid manifest path: {relative}")
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Hash check FAILED: {relative}")
    print(f"PASS: {len(entries)} SHA-256 file hashes")


if __name__ == "__main__":
    main()
