#!/usr/bin/env python3
import sys, os
import numpy as np
import uproot

root_dir = sys.argv[1] if len(sys.argv) > 1 else 'outputs/root'
files = [f for f in os.listdir(root_dir) if f.endswith('.root')]
off = [f for f in files if 'optical_off' in f]
on  = [f for f in files if 'optical_on' in f]
def totals(path):
    t = uproot.open(path)['hodo']
    edep_keys = [k for k in t.keys() if k.startswith('edep_')]
    nph_keys  = [k for k in t.keys() if k.startswith('nph_')]
    edep = np.sum([t[k].array(library='np') for k in edep_keys], axis=0) if edep_keys else np.array([])
    nph  = np.sum([t[k].array(library='np') for k in nph_keys], axis=0) if nph_keys else np.zeros(t.num_entries)
    return edep, nph

print('# Comparison OFF vs ON')
if off:
    e_off, nph_off = totals(os.path.join(root_dir, off[0]))
else:
    e_off, nph_off = np.array([]), np.array([])
if on:
    e_on, nph_on = totals(os.path.join(root_dir, on[0]))
else:
    e_on, nph_on = np.array([]), np.array([])

def mean(x): return float(np.mean(x)) if len(x)>0 else 0.0
def nonzero_frac(x): return float(np.sum(x>0)/len(x)) if len(x)>0 else 0.0

print('mean_edep_off,', mean(e_off))
print('mean_edep_on,',  mean(e_on))
print('mean_nph_off,',  mean(nph_off))
print('mean_nph_on,',   mean(nph_on))
print('frac_nph>0_off,', nonzero_frac(nph_off))
print('frac_nph>0_on,',  nonzero_frac(nph_on))
