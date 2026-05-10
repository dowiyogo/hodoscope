# Iteration 1 Optical Validation — Analysis Execution Log

**Date**: 2026-05-09  
**Branch**: `feat/optical-photon-iteration1`  
**Commit**: `c898dc1`

---

## Commands Executed

```bash
# 1. Inspect ROOT structure
python3 analysis/iteration1_optical_validation/scripts/inspect_optical_root.py \
  analysis/iteration1_optical_validation/outputs/root

# 2. Summarize optical response statistics
python3 analysis/iteration1_optical_validation/scripts/summarize_optical_response.py \
  analysis/iteration1_optical_validation/outputs/root

# 3. Compare OFF vs ON
python3 analysis/iteration1_optical_validation/scripts/compare_optical_off_on.py \
  analysis/iteration1_optical_validation/outputs/root

# 4. Generate detailed validation report
python3 analysis/iteration1_optical_validation/scripts/detailed_analysis.py
```

---

## Files Modified During Analysis

| File | Changes | Reason |
|------|---------|--------|
| `run_iteration1_optical_validation.sh` | Line 52: `cd "$validation_dir"` | Fix ROOT output path |
| `optical_off_center_muon.mac` | Removed duplicate comment line | Fix batch syntax |
| `optical_on_center_muon.mac` | Removed duplicate comment line | Fix batch syntax |
| `optical_on_x_scan.mac` | Changed `/generator/particle` → `/gun/particle` | Fix unknown command |
| `optical_on_y_scan.mac` | Changed `/generator/particle` → `/gun/particle` | Fix unknown command |
| `optical_debug_few_events.mac` | Changed `/generator/particle` → `/gun/particle` | Fix unknown command |
| `ITERATION1_OPTICAL_VALIDATION_SUMMARY.md` | Updated with real analysis data | Generate report |
| `scripts/detailed_analysis.py` | New script | Comprehensive analysis |

---

## ROOT Files Generated

| File | Entries | Status |
|------|---------|--------|
| `optical_off_center_muon.root` | 60 | ✓ |
| `optical_on_center_muon.root` | 60 | ✓ |
| `optical_on_x_scan.root` | 120 | ✓ |
| `optical_on_y_scan.root` | 120 | ✓ |
| `optical_debug_few_events.root` | 6 | ✓ |

---

## Key Metrics Summary

### Per-File Averages

| File | Mean edep [MeV] | Mean nph | Frac nph > 0 |
|------|-----------------|----------|-------------|
| optical_off_center_muon | 0.3654 | 0.000 | 0.000 |
| optical_on_center_muon | 0.3654 | 0.000 | 0.000 |
| optical_on_x_scan | 0.4152 | 0.000 | 0.000 |
| optical_on_y_scan | 0.4009 | 0.000 | 0.000 |
| optical_debug_few_events | 0.3258 | 0.000 | 0.000 |

### OFF vs ON Comparison (center_muon)

```
OFF case: optical_off_center_muon.root (60 events)
ON case: optical_on_center_muon.root (60 events)

mean total edep:   OFF = 0.365421 MeV,  ON = 0.365421 MeV,  Δ = 0.0 (+0.00%)
mean total nph:    OFF = 0.000,         ON = 0.000,         Δ = 0.0
frac nph > 0:      OFF = 0.000,         ON = 0.000,         Δ = 0.0
```

---

## Acceptance Criteria Results

### ✓ PASSED (8/10)

- ✓ ROOT files exist and readable
- ✓ TTree "hodo" exists
- ✓ edep_00...edep_31 branches exist (32)
- ✓ nph_00...nph_31 branches exist (32)
- ✓ edep ON is positive (mean > 0)
- ✓ optical OFF has nph ≈ 0
- ✓ edep OFF and ON do not differ suspiciously (0.00% diff)
- ✓ No batch crashes

### ✗ FAILED (2/10)

- ✗ optical ON has nph > 0 **[FAILED: mean = 0.0]**
- ✗ Fraction events with nph > 0 (ON) **[FAILED: frac = 0.0]**

---

## Final Status

### **PARTIAL PASS**

#### What Works
- ✓ ROOT file generation and I/O
- ✓ Batch macro parsing and execution
- ✓ TTree structure integrity
- ✓ edep branches functional (MIP energy ~0.36 MeV as expected)
- ✓ Runner script path resolution
- ✓ Iteration 0 regression test PASSED

#### What Doesn't Work
- ✗ Optical photon detection (nph = 0 in all cases)
- ✗ No observable SiPM response to optical radiation

#### Conclusion

```
ROOT generation works, but optical photon detection is not yet validated 
because nph remains zero in optical ON.
```

---

## Probable Root Causes (Priority Order)

1. **Scintillation yield = 0 or disabled**
   - Photons not produced by muon dE/dx losses
   - SCINTILLATIONYIELD=10000/MeV may not apply when HODO_ENABLE_OPTICAL=1

2. **EJ-200 optical properties not loaded**
   - RINDEX/ABSLENGTH tables may not parse correctly in Geant4 11.4
   - SCINTILLATIONCOMPONENT1 may not activate

3. **Scintillation process not enabled in steering**
   - G4OpticalPhysics registered but scintillation disabled
   - Check `/process/optical/` commands in macro or PhysicsList

4. **SiPM sensitive detector not receiving photons**
   - SiPMSD::ProcessHits() checks for G4OpticalPhoton but none delivered
   - Photon transport may fail before reaching SiPM volumes

5. **Photon yield capped or transport disabled**
   - `/process/optical/setProcessVerboseLevel` may reveal disabled photon tracking

6. **TiO2 surface absorbs all photons**
   - REFLECTIVITY = 0 or missing in optical surface definition

---

## Recommended Next Diagnostic (Not Yet Implemented)

To identify why nph = 0, run with verbose optical logging:

```bash
export HODO_ENABLE_OPTICAL=1
./build/hodoscope <<'MACRO'
/process/optical/verbose 2
/process/optical/setProcessVerboseLevel 2
/random/setSeeds 1234567 1234568
/analysis/setFileName test_optical_verbose.root
/hodoscope/det/optical 1
/run/initialize
/gun/particle mu-
/gun/energy 4.0 GeV
/gun/position 0.0 0.0 50.0 mm
/gun/direction 0.0 0.0 -1.0
/run/beamOn 1
MACRO
```

This will print scintillation production, photon transport, and absorption events.

---

## Constraints Honored

| Item | Status |
|------|--------|
| src/PhysicsList.cc | NOT MODIFIED |
| src/DetectorConstruction.cc | NOT MODIFIED |
| src/SiPMSD.cc | NOT MODIFIED |
| Geometry changes | NONE |
| Material properties | NOT CHANGED IN CODE |
| Physics changes | NONE |
| Commits made | NO |

---

## Next Steps (User Decision)

**Option A: Debug Optical Physics**
- Implement verbose logging to trace scintillation → photon → SiPM path
- Check why nph stays zero despite HODO_ENABLE_OPTICAL=1
- May require modifications to PhysicsList.cc or DetectorConstruction.cc

**Option B: Close Iteration 1 as Diagnostic**
- Document that infrastructure works but optical physics is inactive
- Archive findings for later implementation
- Move back to Iteration 0 or other development

**User's Decision Required** before proceeding.
