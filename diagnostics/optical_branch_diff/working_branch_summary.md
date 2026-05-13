# Optical photon root cause

## Branch y commit final

- Branch: `feat/optical-photon-iteration1`
- Starting commit: `287231bd8c10781b5ead52412b859d0128a5bfb9`
- Final commit: not created in this working tree

## Hipótesis inicial

Los fotones ópticos se generan correctamente, pero mueren dentro de la barra por la `G4LogicalSkinSurface` `groundfrontpainted` en `Scint_LV`, que cubre también la cara del SiPM. Además, el SiPM tenía un gap de 50 um de aire sin una frontera óptica barra-aire-SiPM.

## Resultado del test unitario

Final unit test:

```text
n_photons_generated: 172809
n_photons_entered_sipm: 14040
n_photons_detected: 14040
detected_over_generated: 0.0812458
```

The isolated test passes the minimum production/coupling/detection checks and the `>5%` efficiency floor.

## Causa identificada

The failure was optical coupling and transport, not scintillation production. The real ROOT tree also exposed that the existing `SiPMSD` is volume-counting, so the robust fix is to let photons enter `SiPM_LV` and be killed by `SiPMSD`, instead of relying on a `dielectric_metal` boundary `Detection` status.

## Fix aplicado

- Added `BUILD_OPTICAL_UNIT_TEST` and the isolated `optical_unit_test` target.
- Added `/hodoscope/det/improvedOptical`, default `false`.
- Preserved the legacy skin-surface behavior when the flag is false.
- Under the flag, removed the 50 um SiPM gap, added scintillator-to-air and scintillator-to-SiPM border surfaces, and gave Si an optical `RINDEX`.
- Kept `src/ScintillatorSD.cc`, `src/SiPMSD.cc`, and the TTree schema unchanged.

## Validación en detector real

Command:

```bash
HODO_ENABLE_OPTICAL=1 ./build/hodoscope macros/optical_tests/run_real_detector_with_improved_optical.mac
```

ROOT analysis:

```text
eventos: 100.0
total nph: 28597
mean nph/evento: 285.97
eventos con nph>0: 100
```

Criteria:

- `mean nph/evento > 50`: pass
- `frac eventos con nph>0 > 0.5`: pass

## Diferencia cuantitativa antes/después

- Before: previous Iteration 1 optical validation reported `mean nph = 0.0` for optical ON.
- After: `mean nph/evento = 285.97`, with `100/100` events having `nph > 0`.

## Archivos modificados y nuevos

Modified by this task:

- `CMakeLists.txt`
- `include/DetectorConstruction.hh`
- `include/DetectorMessenger.hh`
- `src/DetectorConstruction.cc`
- `src/DetectorMessenger.cc`
- `src/RunAction.cc`

New files:

- `diagnostics/optical_photon_root_cause/README.md`
- `diagnostics/optical_photon_root_cause/unit_test_result.md`
- `diagnostics/optical_photon_root_cause/cause_diagnosis.md`
- `diagnostics/optical_photon_root_cause/fix_applied.md`
- `diagnostics/optical_photon_root_cause/summary.md`
- `macros/optical_tests/run_real_detector_with_improved_optical.mac`
- `test_optical/CMakeLists.txt`
- `test_optical/main_optical_unit.cc`
- `test_optical/UnitDetectorConstruction.hh`
- `test_optical/UnitDetectorConstruction.cc`
- `test_optical/UnitSteppingAction.hh`
- `test_optical/UnitSteppingAction.cc`
- `test_optical/macros/unit_test_optical.mac`

## Próximos pasos

Postpone physics refinements to later iterations: PDE calibration, wavelength-dependent SiPM response, dark counts, timing jitter, and validation of diffuse-vs-polished reflector modeling against data.
