# Optical variant ratio debug

## Current issue

- TiO2 mean nph/event = 2.56
- Vikuiti mean nph/event = 32.82
- Vikuiti/TiO2 ratio = 12.8203125

## Reproducibility

| Run mode | TiO2 mean nph/event | Vikuiti mean nph/event | Vikuiti/TiO2 |
|---|---:|---:|---:|
| ST (`HODO_THREADS=1`) | 2.56 | 32.82 | 12.8203125 |
| MT (`HODO_THREADS=8`) | 2.56 | 32.82 | 12.8203125 |

ST and MT are identical for the fixed seed and 100-event quick macros. The high ratio is not a threading or ntuple-merging artifact.

## Reflector debug matrix

| Mode | Surface | R(lambda) | mean nph/event | Ratio note |
|---|---|---|---:|---|
| 1 | diffuse `groundfrontpainted`, `dielectric_dielectric` | TiO2 | 2.56 | baseline |
| 2 | diffuse `groundfrontpainted`, `dielectric_dielectric` | ESR | 32.158 | mode2/mode1 = 12.56171875 |
| 3 | specular `polishedfrontpainted`, `dielectric_metal` | TiO2 | 2.44 | mode3/mode1 = 0.953125 |
| 4 | specular `polishedfrontpainted`, `dielectric_metal` | ESR | 32.432 | mode4/mode3 = 13.29180328 |

The total effect `mode4/mode1` is 12.66875.

## Boundary status

No dedicated OpBoundary counter was added in this pass. A new always-on stepping action would be more invasive than needed for the primary ratio diagnosis. One-event verbose macros were added for future targeted traces:

- `macros/optical_tests/boundary_debug_tio2_1event.mac`
- `macros/optical_tests/boundary_debug_vikuiti_1event.mac`

## Surface semantics audit

In improved-optical mode, `DefineOpticalSurfaces()` does not create the legacy `G4LogicalSkinSurface` on `Scint_LV`. It creates:

- `Scint_PV -> Assembly_PV` reflector border surfaces;
- `Scint_PV -> SiPM_PV` polished SiPM coupling border surfaces.

The readout face should therefore see the SiPM coupling border rather than the reflector. No surface-ordering bug was identified that explains the high ratio.

## Root cause of high ratio

Primary classification: reflectivity-driven photon survival over many bounces.

The ratio is not dominated by diffuse versus specular angularity in the current simplified model. Holding angularity fixed and changing only `R(lambda)` gives a factor of 12.56 in diffuse mode and 13.29 in specular mode. Holding TiO2 reflectivity fixed and changing diffuse to specular gives a factor of 0.95.

So the likely cause is that the current TiO2 reflectivity spectrum is very lossy after many reflections, while ESR reflectivity preserves photons long enough to reach the SiPM. This may be physically plausible for a many-bounce light guide, but it is not calibrated and should not be forced into the preliminary 1.3-2.0 range by tuning reflectivity.

## Recommendation

Do not tune reflectivity values to match the preliminary ratio. Next:

1. Add a boundary-status stepping diagnostic behind a flag.
2. Scan longitudinal source position to estimate bounce-count sensitivity.
3. Study `type`, `finish`, `sigmaAlpha`, and `R(lambda)` separately with more modes.
4. Revisit bidirectional SiPM coupling border surfaces before interpreting absolute `nph`.
5. Compare against experimental light-yield ratios before changing nominal reflector values.

## Files changed

- `hodoscope.cc`
- `include/DetectorConstruction.hh`
- `include/DetectorMessenger.hh`
- `src/DetectorConstruction.cc`
- `src/DetectorMessenger.cc`
- `analysis/iteration1_optical_validation/compare_reflector_debug_modes.C`
- `macros/optical_tests/ratio_debug_mode1_tio2R_diffuse.mac`
- `macros/optical_tests/ratio_debug_mode2_esrR_diffuse.mac`
- `macros/optical_tests/ratio_debug_mode3_tio2R_specular.mac`
- `macros/optical_tests/ratio_debug_mode4_esrR_specular.mac`
- `macros/optical_tests/boundary_debug_tio2_1event.mac`
- `macros/optical_tests/boundary_debug_vikuiti_1event.mac`
- `diagnostics/optical_variant_ratio_debug/`

## Commands executed

```sh
cmake -S . -B build 2>&1 | tee diagnostics/optical_variant_ratio_debug/logs/cmake.log
cmake --build build -j 2 2>&1 | tee diagnostics/optical_variant_ratio_debug/logs/build.log
cmake --build build -j 2 2>&1 | tee diagnostics/optical_variant_ratio_debug/logs/build_after_hodo_threads.log

HODO_THREADS=1 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=1 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
root -l -b -q analysis/iteration1_optical_validation/compare_variant_nph.C

HODO_THREADS=8 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=8 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
root -l -b -q analysis/iteration1_optical_validation/compare_variant_nph.C

HODO_THREADS=8 ./build/hodoscope macros/optical_tests/ratio_debug_mode1_tio2R_diffuse.mac
HODO_THREADS=8 ./build/hodoscope macros/optical_tests/ratio_debug_mode2_esrR_diffuse.mac
HODO_THREADS=8 ./build/hodoscope macros/optical_tests/ratio_debug_mode3_tio2R_specular.mac
HODO_THREADS=8 ./build/hodoscope macros/optical_tests/ratio_debug_mode4_esrR_specular.mac
root -l -b -q analysis/iteration1_optical_validation/compare_reflector_debug_modes.C
```

## Fix status

No optical model fix was applied. This commit adds diagnostic infrastructure and fixes the diagnostic thread-count control by honoring `HODO_THREADS`.

## Final conclusion

The high Vikuiti/TiO2 ratio was reproducible in ST and MT. The 2x2 reflector matrix shows that the effect is dominated by reflectivity: replacing the TiO2 reflectivity set with the ESR reflectivity set gives a factor of about 12.56-13.29 even when the angular model is held fixed.

The diffuse/specular change by itself does not explain the factor in this test; with TiO2 reflectivity fixed, changing diffuse to specular gives a ratio of about 0.95. The result is therefore treated as a feature of the current optical model, not as a transport, threading, TTree, or SiPMSD bug.

The numerical value of the ratio remains uncalibrated. The natural next step is to measure sensitivity to `R(lambda)` and estimate the effective number of optical boundary interactions before tuning any reflectivity or roughness values.
