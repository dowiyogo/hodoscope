# Iteration 0 Validation Summary

## Metadata

| Field | Value |
| --- | --- |
| Execution date | 2026-05-10T01:16:32Z |
| Branch | feat/multithreading |
| Commit | 4a23ff3 |
| Geant4 version | 11.4.0 |
| ROOT files generated | 6 |
| Total simulated events | 1800 |

## ROOT tree

- Tree name: `hodo`
- Entries (reference file): `120`
- Branch count: `104`
- Branches: `eventID, prim_x, prim_y, prim_z, prim_px, prim_py, prim_pz, prim_E, edep_00, edep_01, edep_02, edep_03, edep_04, edep_05, edep_06, edep_07, edep_08, edep_09, edep_10, edep_11, edep_12, edep_13, edep_14, edep_15, edep_16, edep_17, edep_18, edep_19, edep_20, edep_21, edep_22, edep_23, edep_24, edep_25, edep_26, edep_27, edep_28, edep_29, edep_30, edep_31, nph_00, nph_01, nph_02, nph_03, nph_04, nph_05, nph_06, nph_07, nph_08, nph_09, nph_10, nph_11, nph_12, nph_13, nph_14, nph_15, nph_16, nph_17, nph_18, nph_19, nph_20, nph_21, nph_22, nph_23, nph_24, nph_25, nph_26, nph_27, nph_28, nph_29, nph_30, nph_31, tfirst_00, tfirst_01, tfirst_02, tfirst_03, tfirst_04, tfirst_05, tfirst_06, tfirst_07, tfirst_08, tfirst_09, tfirst_10, tfirst_11, tfirst_12, tfirst_13, tfirst_14, tfirst_15, tfirst_16, tfirst_17, tfirst_18, tfirst_19, tfirst_20, tfirst_21, tfirst_22, tfirst_23, tfirst_24, tfirst_25, tfirst_26, tfirst_27, tfirst_28, tfirst_29, tfirst_30, tfirst_31`

## Metrics by run

| Tag | Entries | Mean edep [MeV] | Active bars | Fraction edep>0 | Mean first-hit [ns] | Dominant bar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| validate_center_muon_ST | 120 | 0.361614 | 2.083 | 1.0000 | 0.160164 | 11 |
| validate_center_muon_MT | 120 | 0.371954 | 2.083 | 1.0000 | 0.160164 | 27 |
| validate_x_scan_ST | 390 | 0.449541 | 2.528 | 1.0000 | 0.152464 | 27 |
| validate_x_scan_MT | 390 | 0.454211 | 2.533 | 1.0000 | 0.152464 | 27 |
| validate_y_scan_ST | 390 | 0.457975 | 2.526 | 1.0000 | 0.160153 | 11 |
| validate_y_scan_MT | 390 | 0.448716 | 2.546 | 1.0000 | 0.160164 | 11 |

## ST vs MT comparison

| Tag | Same branches | Dominant bar match | Compatible | KS distance total edep | KS distance active bars | KS distance first hit |
| --- | --- | --- | --- | ---: | ---: | ---: |
| center_muon | true | false | true | 0.108333 | 0.008333 | 0.041667 |
| x_scan | true | true | true | 0.035897 | 0.005128 | 0.000000 |
| y_scan | true | true | true | 0.046154 | 0.023077 | 0.002564 |

## Warnings

- No structural or statistical warnings were detected by the default checks.

## Conclusion

Iteration 0 validation status: PASS.

The suite stays within the non-optical Iteration 0 scope and provides a reproducible baseline for the transition to Iteration 1.

## Files of interest

- `analysis/iteration0_validation/outputs/root/`
- `analysis/iteration0_validation/outputs/tables/`
- `analysis/iteration0_validation/outputs/figures/`
- `analysis/iteration0_validation/outputs/logs/`
