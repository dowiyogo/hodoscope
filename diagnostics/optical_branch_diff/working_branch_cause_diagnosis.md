# Cause diagnosis

Date: 2026-05-12

## Observations

The isolated unit test produced optical photons immediately:

```text
n_photons_generated > 0
```

That rules out `G4OpticalPhysics`, `G4Scintillation`, and the EJ-200 MPT as the primary cause.

The first direct-coupling unit iteration with a painted diffuse boundary and `dielectric_metal` SiPM detection produced nonzero boundary detections, but only:

```text
detected_over_generated = 0.00064291
```

Switching the non-SiPM reflector path to `polishedfrontpainted` raised the unit transport efficiency above the 5% floor. However, the real detector ROOT output still remained low when the SiPM boundary used `dielectric_metal + Detection`, because the production TTree is filled from the existing volume-based `SiPMSD::ProcessHits`.

## Identified cause

The original `nph=0` behavior is caused by optical transport/coupling, not by photon production:

1. The legacy `G4LogicalSkinSurface` on `Scint_LV` paints every face, including the SiPM coupling face.
2. The legacy SiPM placement has a 50 um air gap and no optical border chain that couples scintillator to SiPM.
3. A `dielectric_metal` boundary can produce `G4OpBoundaryProcess` `Detection` statuses, but it does not robustly exercise the existing volume-counting `SiPMSD` path used by the ROOT tree.

## Fix direction

Use the existing `SiPMSD` as designed: let optical photons enter `SiPM_LV`, where `SiPMSD::ProcessHits` counts and kills them. This requires:

- direct bar-SiPM contact when the improved flag is enabled,
- border surfaces from each scintillator physical volume to parent air for the reflector,
- a polished `dielectric_dielectric` border from each scintillator physical volume to its SiPM physical volume,
- no change to `src/SiPMSD.cc` and no new TTree branches.
