# Optical variant comparison: TiO2 vs Vikuiti ESR

## Branch and commit

- branch: `feat/multithreading`
- initial commit: `f27528813032ff6ec22b33bdd76cf0da3f2d3bb7`
- final commit, si aplica: recorded in the final task report after commit creation

## Motivation

The previous optical-photon root-cause work reported nonzero `nph` in the unit test and in the real detector, so the physical difference between reflector variants should be observable once that coupling fix is present on the active branch.

This branch-local validation did not reproduce the nonzero `nph` precondition: both quick ROOT outputs contain zero counted photons. The variant-specific reflector model is implemented, but the collection comparison is not yet physically observable in this branch state.

## Code changes

- `src/DetectorConstruction.cc`: `DefineOpticalSurfaces()` now branches on `fVariant`.
- `macros/optical_tests/run_variant_tio2_quick.mac`: quick Hod2019/TiO2 optical run.
- `macros/optical_tests/run_variant_vikuiti_quick.mac`: quick Hod2018/Vikuiti optical run.
- `analysis/iteration1_optical_validation/compare_variant_nph.C`: ROOT macro that compares `nph_00` through `nph_31`.
- `diagnostics/optical_variant_comparison/`: documentation, log extracts, and comparison output.

## Optical model

| Variant | Type | Finish | SigmaAlpha | Reflectivity |
| --- | --- | --- | --- | --- |
| Hod2019 TiO2 | `dielectric_dielectric` | `groundfrontpainted` | `0.10` | `0.97,0.96,0.93,0.85` |
| Hod2018 Vikuiti | `dielectric_metal` | `polishedfrontpainted` | `0.02` | `0.990,0.990,0.985,0.970` |

The reflector `EFFICIENCY` is zero for both variants. Photon detection remains a SiPM/border-surface concept, not reflector PDE.

## Commands executed

```bash
git branch --show-current
git status -sb
git fetch origin
git status -sb
git pull --rebase origin feat/multithreading
git log --oneline --decorate -5
git diff --stat
git diff --name-only
cmake -S . -B build 2>&1 | tee diagnostics/optical_variant_comparison/logs/cmake.log
cmake --build build -j 2 2>&1 | tee diagnostics/optical_variant_comparison/logs/build.log
./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac 2>&1 | tee diagnostics/optical_variant_comparison/logs/run_variant_tio2_quick.log
./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac 2>&1 | tee diagnostics/optical_variant_comparison/logs/run_variant_vikuiti_quick.log
root -l -b -q analysis/iteration1_optical_validation/compare_variant_nph.C 2>&1 | tee diagnostics/optical_variant_comparison/logs/compare_variant_nph.log
```

## Results

```text
Optical variant nph comparison

TiO2:
  file: diagnostics/optical_variant_comparison/outputs/variant_tio2_quick.root
  tree: hodo
  events: 100
  total_nph: 0
  mean_nph_per_event: 0
  max_nph_per_event: 0
  events_with_nph_gt_0: 0
  fraction_events_with_nph_gt_0: 0

Vikuiti:
  file: diagnostics/optical_variant_comparison/outputs/variant_vikuiti_quick.root
  tree: hodo
  events: 100
  total_nph: 0
  mean_nph_per_event: 0
  max_nph_per_event: 0
  events_with_nph_gt_0: 0
  fraction_events_with_nph_gt_0: 0

ratio_mean_vikuiti_over_tio2: inf
vikuiti_gt_tio2: false
ratio_in_expected_range_1p3_to_2p0: false
```

## Interpretation

Vikuiti did not produce more counted photons than TiO2 in this branch-local quick validation because both variants produced `mean_nph_per_event = 0`.

The ratio is not in the expected `[1.3, 2.0]` range. Since TiO2 has zero mean, the computed ratio is infinite and not physically useful.

The optical-surface branch is observable in the logs: TiO2 selects the diffuse `groundfrontpainted` surface, and Vikuiti selects the specular `polishedfrontpainted` surface. The photon-count difference is not observable in ROOT yet.

No relevant warnings or errors appeared in the log extracts. Geometry overlap checks for the SiPM placements reported `OK`.

Likely causes for zero counted photons in this branch-local validation:

- the `G4LogicalSkinSurface` still paints all faces of `fScintLV`, including the SiPM-facing face;
- the bar-to-SiPM coupling fix from the previous optical root-cause work is not present on this branch;
- the air gap and missing dedicated scintillator-to-SiPM `G4LogicalBorderSurface` can still prevent detection;
- SiPM PDE, optical yield, Birks settings, and absorption length remain simplified and may need a controlled follow-up scan.

## Limitations

- reflector and Kapton are not represented as physical volumes;
- the skin surface is still applied to all `fScintLV`;
- the face toward the SiPM may require a dedicated `G4LogicalBorderSurface` in a later iteration;
- no timing resolution is modeled;
- no electronics response is modeled.

## Next steps

1. Refine the bar-SiPM optical coupling with a dedicated `G4LogicalBorderSurface`.
2. Run a longitudinal position scan after nonzero `nph` is restored on this branch.
3. Sweep TiO2 and Vikuiti reflectivity parameters without tuning to force a target ratio.
4. Validate the final optical response against experimental data if available.
