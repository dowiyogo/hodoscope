# Optical photon to MPPC quickcheck

- Date: 2026-05-12
- Branch: feat/multithreading
- Commit: 0de6db1
- Objective: diagnose why optical photons are not reaching or being counted by the MPPC/SiPM path.
- Macro used: `macros/optical_tests/run_optical_quickcheck.mac`
- Events: 10
- Expected result: optical photons are generated, transported, and at least some are counted by the SiPM SD.
- Observed result: pending run.

## Hypotheses to check

- H1. Optical physics is not registered in `PhysicsList`.
- H2. The scintillator material is missing complete optical properties.
- H3. Muons deposit energy but no optical photons are generated.
- H4. Photons are generated but are killed at boundaries or by the reflector model.
- H5. Photons reach the MPPC geometry but the SiPM SD does not count them.
- H6. Geometry placement or overlap prevents photons from reaching the MPPC.
