# Instrument response code audit

- Branch at audit time: `test/optical-variant-16threads`
- Scope: current single-module hodoscope Geant4 model and 16-thread optical validation branch.

## Detector variants

The detector variants are declared in `include/DetectorConstruction.hh` as:

- `HodoscopeVariant::Hod2019_TiO2`
- `HodoscopeVariant::Hod2018_Vikuiti`

`src/DetectorConstruction.cc` maps those variants into `HodoscopeVariantConfig` records. Both variants use:

- Scintillator: `BC408 (implemented as EJ200-equivalent)`
- MPPC model label: `S12572-100P`
- The current implementation does not create separate physical reflector layers; the reflector is modeled by optical surfaces.

## Physical difference between variants

`Hod2019_TiO2` uses `TiO2OpticalEpoxyPaint` with the `optical_surface_only` reflector model. In the current optical-surface implementation this is a diffuse `groundfrontpainted` surface with wavelength-dependent reflectivity representative of white TiO2 paint.

`Hod2018_Vikuiti` uses `VikuitiESR` with the `thin_passive_layer_or_surface` reflector model. In the current optical-surface implementation this is a more specular ESR-like surface with higher reflectivity near the EJ200 emission peak.

## Optical activation

The optical comparison macros activate optical transport with:

```text
/hodoscope/det/optical true
/hodoscope/det/improvedOptical true
```

They select the variants with:

```text
/hodoscope/setDetectorVariant Hod2019
/hodoscope/setDetectorVariant Hod2018
```

The macros also set the internal module plane separation:

```text
/hodoscope/det/setD 5.0 mm
```

## Meaning of nph_NN

`src/SiPMSD.cc` counts only Geant4 optical photons entering a SiPM/MPPC volume. Each optical photon increments `HodoscopeHit::nPhotons` for the SiPM copy number and is then killed. `src/EventAction.cc` writes those counters into the ROOT branches `nph_00` ... `nph_31`.

Therefore `nph_NN` means optical photons collected by the idealized MPPC volume for channel `NN`. It does not include real S12572-100P PDE, pixel saturation, cross-talk, afterpulsing, dark noise, gain, discriminator behavior, electronics, or pulse shape.

## ROOT branches

`src/RunAction.cc` creates a ROOT TTree named `hodo` with:

- Primary state: `eventID`, `prim_x`, `prim_y`, `prim_z`, `prim_px`, `prim_py`, `prim_pz`, `prim_E`
- Energy deposition per bar: `edep_00` ... `edep_31` in MeV
- Ideal optical photons collected by MPPC volumes: `nph_00` ... `nph_31`
- First hit time per bar: `tfirst_00` ... `tfirst_31` in ns

`src/EventAction.cc` fills these branches once per event from the scintillator and SiPM hit collections.

## Channel geometry used by analysis

The current module has 32 bars:

- `0..7`: X upper subplane
- `8..15`: X lower subplane, shifted by `+2 mm` in X
- `16..23`: Y upper subplane
- `24..31`: Y lower subplane, shifted by `+2 mm` in Y

The nominal local bar pitch is `4 mm`; upper-plane bar centers are `-14, -10, -6, -2, 2, 6, 10, 14 mm`. Lower-plane centers are shifted to `-12, -8, -4, 0, 4, 8, 12, 16 mm`.

The spatial analysis in this stage uses these channel centers as a first-pass centroid model.

## Important angular-resolution limitation

The current repository models one hodoscope module with four subplanes. It does not, in this branch, instantiate two complete hodoscopes simultaneously with a configurable longitudinal baseline.

For that reason this stage must not claim a full telescope angular-resolution simulation. The angular resolution reported here is parametric:

```text
sigma_theta_x = sqrt(sigma_x_Hod2018^2 + sigma_x_Hod2019^2) / L
sigma_theta_y = sqrt(sigma_y_Hod2018^2 + sigma_y_Hod2019^2) / L
```

where `L` is the longitudinal distance between the active centers reconstructed for two complete hodoscopes, conceptually Hodo2018 and Hodo2019. `L` is not the internal `D = 5 mm` separation between X and Y planes inside one module.

A direct Geant4 telescope angular resolution requires a later geometry with two complete modules mounted simultaneously.
