# Fix applied

Date: 2026-05-12

## Unit-test fix

The isolated test now uses:

- EJ-200 MPT copied from the real detector.
- Air and Si with optical `RINDEX`.
- Direct contact between bar and SiPM.
- A painted border from scintillator to world air.
- A polished `dielectric_dielectric` border from scintillator to SiPM so photons enter `SiPM_LV` and the SD-style volume counting path can absorb them.
- `polishedfrontpainted` reflector finish in the improved optical path. The first `groundfrontpainted` iteration transported photons, but the efficiency was only `0.064%`, below the required 5% floor for this diagnostic.

Final unit efficiency:

```text
detected_over_generated: 0.0812458
```

## Real-detector fix

The production detector now has an opt-in flag:

```text
/hodoscope/det/improvedOptical true|false
```

Default is `false`, preserving the legacy Iteration 0 geometry and optical-surface behavior.

When enabled:

- the SiPM gap is removed only for the improved path,
- scintillator and SiPM physical-volume pairs are stored,
- the legacy `SkinSurface` path is skipped,
- each scintillator gets a border surface to assembly air,
- each scintillator gets a polished `dielectric_dielectric` border to its SiPM,
- Si gets `RINDEX=3.5`,
- logical volumes are rebuilt when the flag is toggled after `/run/initialize`, avoiding stale legacy skin surfaces.

## Focused diff stat

```text
CMakeLists.txt                  |  5 +++
include/DetectorConstruction.hh |  8 ++++
include/DetectorMessenger.hh    |  2 +
src/DetectorConstruction.cc     | 85 ++++++++++++++++++++++++++++++++++-------
src/DetectorMessenger.cc        | 11 +++++-
src/RunAction.cc                |  6 ++-
6 files changed, 101 insertions(+), 16 deletions(-)
```

## Diff by file

The complete working-tree diff is intentionally left in git for review with:

```bash
git diff -- CMakeLists.txt include/DetectorConstruction.hh include/DetectorMessenger.hh src/DetectorConstruction.cc src/DetectorMessenger.cc src/RunAction.cc
git diff --no-index /dev/null test_optical/CMakeLists.txt
git diff --no-index /dev/null test_optical/main_optical_unit.cc
git diff --no-index /dev/null test_optical/UnitDetectorConstruction.hh
git diff --no-index /dev/null test_optical/UnitDetectorConstruction.cc
git diff --no-index /dev/null test_optical/UnitSteppingAction.hh
git diff --no-index /dev/null test_optical/UnitSteppingAction.cc
git diff --no-index /dev/null test_optical/macros/unit_test_optical.mac
git diff --no-index /dev/null macros/optical_tests/run_real_detector_with_improved_optical.mac
```
