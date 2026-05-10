# Iteration 1 Optical Validation Report

## Metadata

- **Date**: 2026-05-09 22:58:29
- **Branch**: `feat/optical-photon-iteration1`
- **Commit**: `c898dc1`
- **Geant4 Version**: Geant4 11.4.0
- **ROOT Directory**: `analysis/iteration1_optical_validation/outputs/root`
- **ROOT Files Found**: 5

## ROOT File Inventory

| File | Entries | Total Branches | edep | nph | tfirst |
|------|---------|-----------------|------|-----|--------|
| `optical_debug_few_events.root` | 6 | 104 | 32 | 32 | 32 |
| `optical_off_center_muon.root` | 60 | 104 | 32 | 32 | 32 |
| `optical_on_center_muon.root` | 60 | 104 | 32 | 32 | 32 |
| `optical_on_x_scan.root` | 120 | 104 | 32 | 32 | 32 |
| `optical_on_y_scan.root` | 120 | 104 | 32 | 32 | 32 |

## Per-File Statistics

### optical_debug_few_events.root

- Entries: 6
- Mean total edep: 0.325824 MeV
- Mean active edep bars: 0.406
- Mean total nph: 0.000
- Fraction events with nph > 0: 0.000000
- Mean bars with nph > 0: 0.000
- Dominant edep bar: `edep_11`
- Dominant nph bar: `nph_00`

### optical_off_center_muon.root

- Entries: 60
- Mean total edep: 0.365421 MeV
- Mean active edep bars: 3.938
- Mean total nph: 0.000
- Fraction events with nph > 0: 0.000000
- Mean bars with nph > 0: 0.000
- Dominant edep bar: `edep_11`
- Dominant nph bar: `nph_00`

### optical_on_center_muon.root

- Entries: 60
- Mean total edep: 0.365421 MeV
- Mean active edep bars: 3.938
- Mean total nph: 0.000
- Fraction events with nph > 0: 0.000000
- Mean bars with nph > 0: 0.000
- Dominant edep bar: `edep_11`
- Dominant nph bar: `nph_00`

### optical_on_x_scan.root

- Entries: 120
- Mean total edep: 0.415234 MeV
- Mean active edep bars: 8.000
- Mean total nph: 0.000
- Fraction events with nph > 0: 0.000000
- Mean bars with nph > 0: 0.000
- Dominant edep bar: `edep_27`
- Dominant nph bar: `nph_00`

### optical_on_y_scan.root

- Entries: 120
- Mean total edep: 0.400855 MeV
- Mean active edep bars: 7.938
- Mean total nph: 0.000
- Fraction events with nph > 0: 0.000000
- Mean bars with nph > 0: 0.000
- Dominant edep bar: `edep_17`
- Dominant nph bar: `nph_00`

## OFF vs ON Comparison

**OFF case**: `optical_off_center_muon.root` (60 events)

**ON case**: `optical_on_center_muon.root` (60 events)

| Metric | OFF | ON | Difference |
|--------|-----|----|-----------|
| mean total edep [MeV] | 0.365421 | 0.365421 | +0.000000 (+0.00%) |
| mean total nph | 0.000 | 0.000 | +0.000 |
| frac events nph > 0 | 0.000000 | 0.000000 | +0.000000 |

## Acceptance Criteria

### ✓ PASSED
- ROOT files exist and readable: **YES**
- TTree "hodo" exists: **YES**
- edep_00...edep_31 branches exist: **YES** (32 branches)
- nph_00...nph_31 branches exist: **YES** (32 branches)
- edep ON is positive: **YES** (mean > 0)
- optical OFF has nph ≈ 0: **YES** (mean = 0.0)
- edep OFF and ON do not differ suspiciously: **YES** (diff = 0.0, rel diff = 0.00%)
- No batch crashes: **YES**

### ✗ FAILED
- optical ON has nph > 0: **NO** (mean = 0.0)
- Fraction events with nph > 0 (ON): **NO** (frac = 0.0)

## Conclusion

**Status: PARTIAL PASS**

ROOT file generation and batch infrastructure working correctly. However, optical photon detection is not yet active:

```
ROOT generation works, but optical photon detection is not yet validated because nph remains zero in optical ON.
```

### Likely Causes (in order of probability):
1. G4OpticalPhysics registered but scintillation yield is zero or disabled
2. EJ-200 optical properties (RINDEX, ABSLENGTH) not properly loaded for 11.4
3. G4OpticalPhoton transport incomplete or yield disabled in steering
4. SiPM sensitive detector not connected to optical photon tracking
5. Scintillation process not triggered for muon dE/dx losses
6. TiO2 surface or optical properties absorption too high

### Next Steps (recommended, NOT implemented):
1. Verify G4OpticalPhysics activation in PhysicsList with verbose logging
2. Check scintillation yield in EJ-200 material definition
3. Enable G4OpticalPhysics verbose output: `/process/optical/verbose 2`
4. Add photon counter to RunAction edep collection
5. Check that scintillation is enabled in steering, not just registered
