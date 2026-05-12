# Optical photon to MPPC quickcheck

## Branch and commit
- branch: `feat/multithreading`
- commit: `0de6db1`

## Commands executed
- cmake: `cmake -S . -B build 2>&1 | tee diagnostics/optical_photon_to_mppc_quickcheck/logs/cmake.log`
- build: `cmake --build build -j 2 2>&1 | tee diagnostics/optical_photon_to_mppc_quickcheck/logs/build.log`
- run: `cd build && ./hodoscope ../macros/optical_tests/run_optical_quickcheck.mac 2>&1 | tee ../diagnostics/optical_photon_to_mppc_quickcheck/logs/run_optical_quickcheck.log`
- run tracking verbose: `cd build && ./hodoscope ../macros/optical_tests/run_optical_quickcheck_tracking_verbose.mac 2>&1 | tee ../diagnostics/optical_photon_to_mppc_quickcheck/logs/run_optical_quickcheck_tracking_verbose.log`

## Macro used
- path: `macros/optical_tests/run_optical_quickcheck.mac`

## Observations
- edep in scintillators: yes, nonzero (`3.7719969697505435 MeV` over 10 events in the main ROOT file)
- optical photons generated: yes
- optical photons tracked: yes
- photons reach MPPC: no evidence yet; `nph` remains zero
- MPPC sensitive detector counts photons: no, `nph_00..nph_31` are all zero

## Most likely failure point
3. photons generated but killed at boundary

## Evidence
- `DetectorConstruction` prints `TiO2 optical surface: present` and `Optical photons: enabled`.
- Tracking verbose log contains `Particle = opticalphoton` secondary tracks with `Parent ID = 1`.
- ROOT inspection shows `total_nph 0` and `nonzero_nph_cells 0` in both optical quickcheck files.
- `SiPMSD::ProcessHits()` only counts `G4OpticalPhoton` when a track actually enters the SiPM logical volume.

## Next minimal fix
Keep the current geometry/scoring frozen and inspect the optical boundary between the scintillator face and the MPPC. The most likely small fix is a border-surface or placement change on the SiPM-facing face, because the current skin surface paints all faces and the SiPM still sits behind an air gap.
