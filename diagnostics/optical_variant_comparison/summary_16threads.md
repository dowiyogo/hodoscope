# Optical variant comparison, 16 threads

- Rama: `test/optical-variant-16threads`
- Commit: `b6e27b5` (`b6e27b5cdeb51d2f78f20290f9c0e3cfe804e54c`)
- Threads: `16`
- Backend de analisis: `uproot`
- Build: `success`
- ROOT esperados generados: `yes`

## Comandos ejecutados

```bash
git switch feat/multithreading
git pull --ff-only
git switch -c test/optical-variant-16threads
rm -rf build
cmake -S . -B build
cmake --build build -j 16
mkdir -p diagnostics/optical_variant_comparison/outputs
HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
python3 analysis/optical_variant_nph_summary.py --threads 16 --build-status success --warning 'Geant4 Run10035 warning in both 16-thread quick runs: Event modulo reduced to 6 from 10 to distribute 100 events across 16 threads; runs completed successfully.'
```

## Comparacion

| Variante | Entries | Mean total nph/event | Std | Median | Frac. nph > 0 | Mean active channels/event |
|---|---:|---:|---:|---:|---:|---:|
| TiO2 | 100 | 2.56 | 1.99158 | 2 | 0.9 | 1.35 |
| Vikuiti | 100 | 32.82 | 12.2257 | 30 | 1 | 2.04 |

- Ratio mean_nph_Vikuiti / mean_nph_TiO2: `12.8203`

## Channel means

| Canal | TiO2 mean nph | Vikuiti mean nph |
|---|---:|---:|
| nph_00 | 0 | 0 |
| nph_01 | 0 | 0 |
| nph_02 | 0 | 0.17 |
| nph_03 | 0 | 0 |
| nph_04 | 0 | 0 |
| nph_05 | 0 | 0 |
| nph_06 | 0 | 0 |
| nph_07 | 0 | 0 |
| nph_08 | 0 | 0 |
| nph_09 | 0 | 0 |
| nph_10 | 0 | 0 |
| nph_11 | 1.11 | 15.68 |
| nph_12 | 0 | 0 |
| nph_13 | 0 | 0 |
| nph_14 | 0 | 0 |
| nph_15 | 0 | 0 |
| nph_16 | 0 | 0 |
| nph_17 | 0 | 0 |
| nph_18 | 0 | 0 |
| nph_19 | 0.06 | 0.03 |
| nph_20 | 0 | 0.22 |
| nph_21 | 0 | 0.13 |
| nph_22 | 0 | 0 |
| nph_23 | 0 | 0 |
| nph_24 | 0 | 0 |
| nph_25 | 0 | 0 |
| nph_26 | 0 | 0 |
| nph_27 | 1.39 | 16.59 |
| nph_28 | 0 | 0 |
| nph_29 | 0 | 0 |
| nph_30 | 0 | 0 |
| nph_31 | 0 | 0 |

## Criterios de exito

| Criterio | Estado |
|---|---|
| Build exitoso | `success` |
| ROOT TiO2 generado | `ok` |
| ROOT Vikuiti generado | `ok` |
| TTree hodo disponible | `ok` |
| Ramas nph_00 ... nph_31 | `ok` |
| Mean total nph/event > 0 | `ok` |
| Mean Vikuiti > TiO2 | `ok` |
| summary_16threads.md generado | `ok` |

## Interpretacion

nph representa fotones ópticos recolectados idealmente por el volumen MPPC; todavía no incluye PDE real del S12572-100P, saturación de pixeles, cross-talk, afterpulsing, ruido oscuro, ganancia electrónica ni forma de pulso.

## Warnings y limitaciones

- Geant4 Run10035 warning in both 16-thread quick runs: Event modulo reduced to 6 from 10 to distribute 100 events across 16 threads; runs completed successfully.
- PyROOT was not available in this shell, and the ROOT environment emitted `cygpath` warnings during Python checks; the analysis used `uproot` successfully.
