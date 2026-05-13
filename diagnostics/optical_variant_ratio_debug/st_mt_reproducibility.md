# ST vs MT reproducibility

## Commands

```sh
HODO_THREADS=1 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=1 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
root -l -b -q analysis/iteration1_optical_validation/compare_variant_nph.C

HODO_THREADS=8 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=8 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
root -l -b -q analysis/iteration1_optical_validation/compare_variant_nph.C
```

## Result

| Run mode | TiO2 mean nph/event | Vikuiti mean nph/event | Vikuiti/TiO2 |
|---|---:|---:|---:|
| ST (`HODO_THREADS=1`) | 2.56 | 32.82 | 12.8203125 |
| MT (`HODO_THREADS=8`) | 2.56 | 32.82 | 12.8203125 |

The ST and MT results are identical for the fixed seed and 100-event quick macros. The high ratio is therefore not explained by thread-local state, ntuple merging, or random-seed differences.

## Infrastructure note

The first ST attempt showed that `HODO_THREADS` was not honored by `hodoscope.cc`; the executable still launched 8 threads. Diagnostic support for `HODO_THREADS` was added while preserving the existing default of `min(8, hardware_concurrency)`.
