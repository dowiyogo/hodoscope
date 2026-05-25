# TiO2 / TiO2+epoxy optical model audit

- Branch: `test/optical-variant-16threads`
- Scope: central-gun reflector sensitivity study for Hod2019/TiO2+Optical Epoxy Paint.

## Current TiO2 model

The default Hod2019 model is selected with:

```text
/hodoscope/setDetectorVariant Hod2019
```

In `src/DetectorConstruction.cc`, the optical surface uses:

- `G4OpticalSurface` model: `unified`
- Type: `dielectric_dielectric`
- Finish: `groundfrontpainted`
- Sigma alpha: `0.10`
- Energies: `{2.38, 2.70, 2.92, 3.10} eV`
- `REFLECTIVITY`: `{0.97, 0.96, 0.93, 0.85}`
- `EFFICIENCY`: `{0, 0, 0, 0}`

The point `2.92 eV` is approximately the EJ200 emission peak near 425 nm, so the current default effective reflectivity near 425 nm is `R425 = 0.93`.

## Current Vikuiti/ESR model

The Hod2018 model is selected with:

```text
/hodoscope/setDetectorVariant Hod2018
```

The current ESR-like optical surface uses:

- `G4OpticalSurface` model: `unified`
- Type: `dielectric_metal`
- Finish: `polishedfrontpainted`
- Sigma alpha: `0.02`
- Energies: `{2.38, 2.70, 2.92, 3.10} eV`
- `REFLECTIVITY`: `{0.990, 0.990, 0.985, 0.970}`
- `EFFICIENCY`: `{0, 0, 0, 0}`

## Why Hod2019 should be treated as TiO2+epoxy effective

The experimental Hod2019 configuration is not necessarily a pure idealized TiO2 surface. It is better described here as TiO2 plus optical epoxy paint, with an effective optical response that may differ from a bare TiO2 reflectivity table and from the simplified `groundfrontpainted` model.

The production position scan showed that the current default TiO2 model gives much smaller ideal MPPC-volume photon collection than Vikuiti. This sweep is therefore a sensitivity study of effective reflectivity and surface behavior, not a claim about the true material reflectivity.

## Existing commands

The detector already exposes:

- `/hodoscope/setDetectorVariant`
- `/hodoscope/det/optical`
- `/hodoscope/det/improvedOptical`
- `/hodoscope/det/reflectorDebugMode`

`reflectorDebugMode` is a diagnostic override with modes `0..4`. For the TiO2+epoxy sweep, `reflectorDebugMode != 0` has priority over the new effective-reflector commands.

## New sweep commands

This branch adds:

- `/hodoscope/det/tio2EpoxyEffectiveR425 <double>`
- `/hodoscope/det/tio2EpoxySurfaceMode <default|diffuse|specular>`

If no new command is used, Hod2019/TiO2 follows the previous default path. If `tio2EpoxyEffectiveR425 >= 0` and `reflectorDebugMode == 0`, Hod2019 uses an effective TiO2+epoxy reflectivity:

```text
scale = R425 / 0.93
R_eff[i] = min(0.999, R_default[i] * scale)
```

This preserves the rough spectral shape of the default TiO2 table while changing the effective reflectivity near 425 nm.

## Limitation

The new `R425` is an effective model knob. It is not a measured material property and must be calibrated against experimental data before being used as a physical reflector constant.
