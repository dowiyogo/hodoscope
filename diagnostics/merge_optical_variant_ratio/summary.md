# Merge optical variant ratio diagnostics

## Merge result
- source: diag/optical-variant-ratio
- target: feat/multithreading
- method: rebase diag onto feat/multithreading, then fast-forward merge
- generated-output cleanup commit: 46c1c54

## Preserved functionality
- HODO_THREADS=1 for serial-style validation with one Geant4 worker thread.
- HODO_THREADS=8 for MT validation.
- HODO_THREADS=16 for higher-thread MT validation.
- If HODO_THREADS is not defined, the existing safe default behavior is preserved.
- Optical photon detection remains active.
- TiO2 and Vikuiti variants remain differentiated.

## Validation
Build completed successfully with:
- cmake -S . -B build
- cmake --build build -j 2

Optical variant nph merge validation

TiO2 ST mean nph/event: 2.56
Vikuiti ST mean nph/event: 32.82
ratio ST: 12.8203125
TiO2 MT8 mean nph/event: 2.56
Vikuiti MT8 mean nph/event: 32.82
ratio MT8: 12.8203125
TiO2 MT16 mean nph/event: 2.56
Vikuiti MT16 mean nph/event: 32.82
ratio MT16: 12.8203125

TiO2 nph > 0 in ST, MT8, MT16: true
Vikuiti nph > 0 in ST, MT8, MT16: true
Vikuiti > TiO2 in ST, MT8, MT16: true
HODO_THREADS=16 completed without crash: true
ROOT written for 16-thread TiO2 and Vikuiti runs: true

## Notes
- No ROOT committed.
- build/ not committed.
- generated outputs were moved to backup:
  ../hodoscope_untracked_backup_20260514_092620
- no optical tuning was performed.
- no TTree changes were made as part of this merge validation.
- no SiPMSD or ScintillatorSD changes were made as part of this merge validation.
