# Optical variant ratio debug

- Branch: `diag/optical-variant-ratio`
- Base branch: `feat/multithreading`
- Base commit: `06f4c13 Port optical photon detection fix to multithreading branch`

## Problem

Optical photon detection has been recovered in the multithreading branch, but the quick comparison currently gives a large reflector response ratio:

- TiO2: `total_nph = 256`, `mean_nph/event = 2.56`
- Vikuiti ESR: `total_nph = 3282`, `mean_nph/event = 32.82`
- Vikuiti/TiO2 ratio: `12.82`

This is not considered calibrated.

## Goal

Diagnose why the optical model produces such a large Vikuiti/TiO2 ratio by separating:

- reflectivity spectrum effects;
- diffuse versus specular angular response;
- Geant4 optical surface type;
- SiPM coupling and surface precedence effects.

## Rule

Do not tune parameters to force a target ratio. This branch is for diagnosis only unless an objective implementation bug is found.
