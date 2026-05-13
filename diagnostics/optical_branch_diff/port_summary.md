# Port optical photon detection fix to feat/multithreading

## Branches compared

- base: `feat/multithreading` at `2bb0233`
- working optical branch: `feat/optical-photon-iteration1` at `287231b`
- merge base: `4a23ff375b18c98de884330c14edce0054bb8282`
- local work branch: `fix/port-optical-photon-detection-to-mt`

## Problem

`feat/multithreading` had `nph = 0` for both quick optical variant runs even though optical photons and variant surfaces were enabled.

`feat/optical-photon-iteration1` had demonstrated `nph > 0` after the root-cause diagnostic:

- unit test: `n_photons_detected = 14040`
- real detector: `total nph = 28597`
- real detector: `mean nph/evento = 285.97`
- real detector: `100/100` events with `nph > 0`

## Root cause from working branch

The working branch showed that the failure was optical coupling and transport, not scintillation production and not `SiPMSD`.

The legacy `G4LogicalSkinSurface` painted all faces of `Scint_LV`, including the SiPM-facing face, and the SiPM was separated from the bar by a `50 um` air gap without a dedicated optical border chain. The robust fix is to let photons enter `SiPM_LV`, where the existing `SiPMSD::ProcessHits` counts and kills them.

## Minimal changes ported

| Archivo | Cambio portado | Motivo |
| --- | --- | --- |
| `include/DetectorConstruction.hh` | Added `fUseImprovedOpticalCoupling`, getter/setter, `fAssemblyPV`, `fScintPVs`, and `fSiPMPVs`. | Required state for opt-in border surfaces per physical bar/SiPM pair. |
| `include/DetectorMessenger.hh` | Added `/hodoscope/det/improvedOptical`. | Runtime flag, default remains `false`. |
| `src/DetectorMessenger.cc` | Implemented the improved optical command. | Allows macros to enable the ported coupling fix. |
| `src/DetectorConstruction.cc` | Added `RINDEX=3.5` for `G4_Si`. | Gives the SiPM material a valid optical index. |
| `src/DetectorConstruction.cc` | Removed the `50 um` gap only when improved optical is enabled. | Lets photons cross directly into `SiPM_LV` without changing default geometry. |
| `src/DetectorConstruction.cc` | Stored `Scint_PV` and `SiPM_PV` placements. | Required for `G4LogicalBorderSurface` construction. |
| `src/DetectorConstruction.cc` | In improved mode, skipped the global skin and used `Scint -> assembly air` reflector borders plus polished `Scint -> SiPM` borders. | Prevents the reflector from covering the SiPM face and preserves volume-counting in `SiPMSD`. |
| `src/DetectorConstruction.cc` | Kept the existing TiO2/Vikuiti branch in `DefineOpticalSurfaces()`. | Preserves diffuse TiO2 and specular Vikuiti models from `feat/multithreading`. |
| `src/RunAction.cc` | Logged/wrote `improved_optical_coupling` in sidecar config. | Verification only; no TTree schema change. |
| `macros/optical_tests/run_variant_tio2_quick.mac` | Added `/hodoscope/det/improvedOptical true`. | Exercises the ported fix in the TiO2 run. |
| `macros/optical_tests/run_variant_vikuiti_quick.mac` | Added `/hodoscope/det/improvedOptical true`. | Exercises the ported fix in the Vikuiti run. |

## Changes intentionally not ported

| Archivo/cambio | Motivo |
| --- | --- |
| `src/SiPMSD.cc` | Not changed in the working fix; existing volume counting is preserved. |
| `src/ScintillatorSD.cc` | Not needed and explicitly out of scope. |
| `src/PhysicsList.cc` env-gated optical registration | Not the cause root; MT branch already registers optical physics and produced optical tracks. |
| `hodoscope.cc` env logging | Diagnostic only; MT run manager remains untouched. |
| `CMakeLists.txt` / `test_optical/` | Diagnostic unit-test infrastructure, not required for the minimal MT port. |
| Analysis scripts from the optical branch | Avoid mixing unrelated analysis changes. |
| The working branch's polished TiO2 improved reflector choice | Not ported literally because this task must preserve TiO2 diffuse vs Vikuiti specular differentiation. |

## Build result

- cmake: passed
- build: passed

Commands:

```bash
cmake -S . -B build 2>&1 | tee diagnostics/optical_branch_diff/logs/cmake_after_port.log
cmake --build build -j 2 2>&1 | tee diagnostics/optical_branch_diff/logs/build_after_port.log
```

## Optical validation after port

```text
TiO2 total_nph: 256
TiO2 mean_nph/event: 2.56
TiO2 events_with_nph_gt_0: 90
Vikuiti total_nph: 3282
Vikuiti mean_nph/event: 32.82
Vikuiti events_with_nph_gt_0: 100
ratio Vikuiti/TiO2: 12.8203125
```

Both variants now satisfy the minimum criterion `total_nph > 0`.

The desired `ratio` range `[1.3, 2.0]` is not satisfied. No parameters were tuned to force that range.

## MT sanity validation

- macro used: `diagnostics/optical_branch_diff/run_iteration0_sanity_short.mac`
- result: completed in Geant4 MT mode with `8` threads
- events: `20`
- total edep: `8.026836514713077`
- mean edep/event: `0.40134182573565386`
- events with edep > 0: `20`

The run produced a ROOT file and preserved non-optical `edep` writing. The only warning in the short sanity run was Geant4 reducing event modulo for distributing only 20 events across 8 threads.

## Interpretation

`nph > 0` was recovered in `feat/multithreading` with the minimal optical coupling port.

The TiO2/Vikuiti differentiation was preserved: TiO2 uses `dielectric_dielectric + groundfrontpainted`, while Vikuiti uses `dielectric_metal + polishedfrontpainted`.

Vikuiti collected more photons than TiO2 in the quick run, but the ratio is much larger than the expected `[1.3, 2.0]` range. This is qualitatively consistent with a more reflective/specular surface, but quantitatively not yet a calibrated physical model.

Remaining limitations:

- reflector and Kapton are still not modeled as physical volumes;
- SiPM coupling is still simplified;
- no PDE, timing resolution, electronics, dark counts, crosstalk, or afterpulsing are modeled;
- the large ratio likely needs a follow-up scan of border-surface choices and reflector parameters.

## Next steps

1. Investigate why the TiO2/Vikuiti ratio is much larger than `[1.3, 2.0]`.
2. Refine bar-SiPM border-surface modeling in a dedicated iteration.
3. Run a longitudinal position scan.
4. Validate reflector response against experimental data if available.
