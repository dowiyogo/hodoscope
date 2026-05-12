# Variant integration plan

## Files inspected

- `src/DetectorConstruction.cc`
- `include/DetectorConstruction.hh`
- `src/DetectorMessenger.cc`
- `include/DetectorMessenger.hh`
- `src/RunAction.cc`
- `include/RunAction.hh`
- `hodoscope.cc`
- `CMakeLists.txt`
- Macro references in `macros/run_mip_central.mac`, `macros/scan_xy.mac`, `macros/test_setD.mac`, and `analysis/iteration0_validation/macros/*.mac`

## Current ownership map

- Geometry construction: `DetectorConstruction`
- Material definition: `DetectorConstruction::DefineMaterials()`
- Optical surface definition: `DetectorConstruction::DefineOpticalSurfaces()`
- Macro configuration: `DetectorMessenger`
- Run-level output management: `RunAction`

## Current reflector state

- The detector currently models the TiO2 reflector as a `G4OpticalSurface` skin surface on the scintillator.
- The reflector is not a physical volume in Iteration 0.
- Optical surfaces are only active when the optical flag is enabled; by default they are skipped and therefore inert for the current scoring workflow.
- The current code path therefore preserves the Iteration 0 energy-deposit behavior when optical transport remains disabled.

## Proposed changes

1. Introduce a typed detector variant enum in `DetectorConstruction`.
2. Centralize variant configuration in a small struct with the fields needed for Hod2019/TiO2 and Hod2018/Vikuiti.
3. Add a macro command `/hodoscope/setDetectorVariant` that accepts the required names and aliases and translates them to the enum in one place.
4. Keep Hod2019/TiO2 as the default to preserve existing results.
5. Keep the present reflector implementation as a surface-only abstraction by default; do not add a physical Vikuiti/Kapton volume in this iteration.
6. Print the selected variant and its configuration at run start.
7. Write a small sidecar configuration text file next to the ROOT output if the run-action path allows it without touching the TTree.
8. Add minimal test macros for Hod2019 and Hod2018.

## Risks to Iteration 0

- Changing the default variant would alter existing results, so the default must remain Hod2019/TiO2.
- Accidentally coupling variant selection to the active optical flag could change the edep workflow; that must stay disabled by default.
- Introducing a physical Vikuiti/Kapton layer would change material budget and can perturb dE/dx and scattering, so that must remain behind a separate disabled flag or be omitted here.
- Any rename of tree branches or ROOT format changes would break analysis scripts and must be avoided.

## Local hypothesis

- The safest implementation is to keep the geometry and scoring path unchanged, add variant metadata/configuration in `DetectorConstruction`, and expose the choice through the existing messenger without activating optical transport.

## Cheap discriminating check

- Build after the change and run two short macros with optical transport disabled. If the ROOT outputs and branch names remain unchanged while the console reports the selected variant, the implementation is compatible with Iteration 0.
