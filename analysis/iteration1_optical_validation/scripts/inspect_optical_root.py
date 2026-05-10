#!/usr/bin/env python3
import sys
import os
import uproot

root_dir = sys.argv[1] if len(sys.argv) > 1 else 'outputs/root'
files = []
if os.path.isdir(root_dir):
    for f in os.listdir(root_dir):
        if f.endswith('.root'):
            files.append(os.path.join(root_dir, f))

for f in files:
    try:
        t = uproot.open(f)['hodo']
    except Exception as e:
        print(f"{f}: could not open: {e}")
        continue
    print(f"File: {f}")
    print(f" TTree: hodo entries={t.num_entries}")
    keys = list(t.keys())
    print(f" Branches ({len(keys)}): {', '.join(keys)}")
    edep = [k for k in keys if k.startswith('edep_')]
    nph  = [k for k in keys if k.startswith('nph_')]
    tfirst = [k for k in keys if k.startswith('tfirst_')]
    print(f" edep branches: {len(edep)}")
    print(f" nph branches: {len(nph)}")
    print(f" tfirst branches: {len(tfirst)}")
    print()
