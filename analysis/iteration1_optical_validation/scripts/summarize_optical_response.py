#!/usr/bin/env python3
import sys, os
import numpy as np
import uproot

root_dir = sys.argv[1] if len(sys.argv) > 1 else 'outputs/root'
files = [os.path.join(root_dir,f) for f in os.listdir(root_dir) if f.endswith('.root')]
rows = []
for f in files:
    try:
        t = uproot.open(f)['hodo']
    except Exception as e:
        continue
    n = t.num_entries
    # sum edep across edep_XX branches
    edep_keys = [k for k in t.keys() if k.startswith('edep_')]
    nph_keys  = [k for k in t.keys() if k.startswith('nph_')]
    if not edep_keys:
        continue
    edep_arrs = [t[k].array(library='np') for k in edep_keys]
    total_edep = np.sum(edep_arrs, axis=0)
    nph_arrs = [t[k].array(library='np') for k in nph_keys] if nph_keys else [np.zeros(n)]
    total_nph = np.sum(nph_arrs, axis=0)
    mean_edep = float(np.mean(total_edep))
    mean_nph  = float(np.mean(total_nph))
    frac_nonzero = float(np.sum(total_nph>0)/len(total_nph)) if len(total_nph)>0 else 0.0
    rows.append((os.path.basename(f), n, mean_edep, mean_nph, frac_nonzero))

print('file,entries,mean_total_edep,mean_total_nph,frac_events_nph>0')
for r in rows:
    print(','.join(map(str,r)))
