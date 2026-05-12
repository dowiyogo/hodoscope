# Detector Variant Integration Summary

## Changes made

- Added a typed detector variant model in `DetectorConstruction` with `HodoscopeVariant::Hod2019_TiO2` as the default and `HodoscopeVariant::Hod2018_Vikuiti` as the selectable alternative.
- Added a centralized variant configuration struct with reflector, Kapton, scintillator, and MPPC metadata.
- Extended the existing messenger with `/hodoscope/setDetectorVariant` and alias parsing for `Hod2019`, `TiO2`, `Hod2018`, and `Vikuiti` forms.
- Kept the current Iteration 0 scoring path unchanged: no new TTree branches, no digitization, no optical transport activation, and no change to the existing energy-deposit collection.
- Added run-start configuration printing and an optional sidecar metadata file next to the ROOT output.
- Added two minimal macro tests for the two variants.

## Files modified

- `include/DetectorConstruction.hh`
- `src/DetectorConstruction.cc`
- `include/DetectorMessenger.hh`
- `src/DetectorMessenger.cc`
- `src/RunAction.cc`
- `macros/variant_tests/run_hod2019_tio2.mac`
- `macros/variant_tests/run_hod2018_vikuiti.mac`
- `diagnostics/detector_variant_integration/variant_integration_plan.md`

## Build command used

```bash
cd /home/reriosto/d/hodoscope-g4/build && cmake .. 2>&1 | tee ../diagnostics/detector_variant_integration/logs/build.log && make -j 2>&1 | tee -a ../diagnostics/detector_variant_integration/logs/build.log
```

## Macro commands used

```bash
cd /home/reriosto/d/hodoscope-g4/build && ./hodoscope ../macros/variant_tests/run_hod2019_tio2.mac 2>&1 | tee ../diagnostics/detector_variant_integration/logs/run_hod2019_tio2.log
```

```bash
cd /home/reriosto/d/hodoscope-g4/build && ./hodoscope ../macros/variant_tests/run_hod2018_vikuiti.mac 2>&1 | tee ../diagnostics/detector_variant_integration/logs/run_hod2018_vikuiti.log
```

## Outputs

- ROOT outputs:
  - `/home/reriosto/d/hodoscope-g4/build/output_hod2019_tio2.root`
  - `/home/reriosto/d/hodoscope-g4/build/output_hod2018_vikuiti.root`
- Sidecar metadata files:
  - `/home/reriosto/d/hodoscope-g4/build/output_hod2019_tio2_config.txt`
  - `/home/reriosto/d/hodoscope-g4/build/output_hod2018_vikuiti_config.txt`
- Logs:
  - `diagnostics/detector_variant_integration/logs/build.log`
  - `diagnostics/detector_variant_integration/logs/run_hod2019_tio2.log`
  - `diagnostics/detector_variant_integration/logs/run_hod2018_vikuiti.log`

## Physical differences implemented

- The detector now records and prints which variant was selected.
- The selected reflector name, model, thickness, Kapton thickness, and MPPC model are captured as configuration metadata.
- The default Hod2019/TiO2 path continues to represent the reflector as a surface-only abstraction.

## Physical differences only parametrized for now

- No physical Vikuiti or Kapton layer was added.
- No optical photon transport was activated.
- No wavelength-dependent reflectivity or full optical response was introduced.
- The scintillator remains the existing EJ-200-based material, documented as BC408-equivalent for configuration purposes.

## Verification result

- The project compiled successfully.
- Both minimal macros completed successfully.
- The default variant remained Hod2019/TiO2.
- Hod2018/Vikuiti printed the expected variant metadata.
- ROOT outputs were created for both runs.
- Optical photons remained disabled.
- The existing `ScintillatorSD` path was not broken.
- No TTree branch names or output format were changed.

## Recommended next steps for Iteration 1 optical work

1. Split the reflector surface implementation into a variant-aware abstraction before enabling real optical transport.
2. Add a separate, disabled-by-default flag for any future physical Vikuiti/Kapton layers.
3. Introduce variant-specific optical properties tables for BC-408, Vikuiti, and TiO2 only when optical photon transport is intentionally enabled.
4. Keep the current scoring/tree path frozen and validate optical changes against the existing Iteration 0 regression macros.
