# Surface semantics audit

## Intended improved-optical topology

```text
Scintillator volume
  lateral/readout-excluded exits to assembly air -> reflector border surface
  readout face toward SiPM                         -> polished SiPM coupling border
```

## Current Geant4 implementation

- When `/hodoscope/det/optical false`, `DefineOpticalSurfaces()` returns without creating optical surfaces.
- When `/hodoscope/det/improvedOptical false`, a legacy `G4LogicalSkinSurface` is still applied to `Scint_LV`.
- When `/hodoscope/det/improvedOptical true`, no global scintillator skin is created.
- In improved mode, each scintillator physical volume gets a forward `G4LogicalBorderSurface` from `Scint_PV` to `Assembly_PV` using the selected reflector model.
- In improved mode, each scintillator physical volume gets a forward `G4LogicalBorderSurface` from `Scint_PV` to its paired `SiPM_PV` using a polished dielectric-dielectric SiPM coupling surface.

## Surface applied by boundary

| Boundary | Physical-volume pair | Expected surface |
|---|---|---|
| Scintillator to assembly air | `Scint_PV -> Assembly_PV` | TiO2/Vikuiti reflector |
| Scintillator to SiPM | `Scint_PV -> SiPM_PV` | polished SiPM coupling |
| SiPM to scintillator | `SiPM_PV -> Scint_PV` | no explicit reverse border |

## Findings

- The improved-optical path does not leave a global `G4LogicalSkinSurface` on `Scint_LV`, so the readout face is not obviously painted by a skin surface in this mode.
- The `Scint_PV -> SiPM_PV` coupling border should take precedence on the readout face when a photon steps from scintillator into SiPM.
- Only forward border surfaces are defined. For the current SiPM scoring model, photons entering the SiPM are counted/killed, so the missing reverse border is not expected to explain the high Vikuiti/TiO2 ratio.
- The high ratio is reproduced with mode 2 versus mode 1, where both use the same diffuse `groundfrontpainted` surface. This points away from surface ordering and toward survival probability from the reflectivity spectrum.

## Remaining caveat

Geant4 border surfaces are ordered by physical-volume pair. A future coupling refinement should consider defining both directions explicitly if photons are ever allowed to leave the SiPM volume instead of being counted/killed on entry.
