# Optical branch diff

- Base branch: `feat/multithreading`
- Working optical branch: `feat/optical-photon-iteration1`

## Problem

`feat/multithreading` currently builds the optical surfaces and reports optical photons enabled, but the quick ROOT outputs have `nph = 0` for both TiO2 and Vikuiti variants.

`feat/optical-photon-iteration1` previously demonstrated nonzero SiPM photon detection:

- unit test: `n_photons_detected = 14040`
- real detector: `total nph = 28597`
- real detector: `mean nph/evento = 285.97`
- real detector: `100/100` events with `nph > 0`

## Objective

Identify the minimal real fix that made optical photon detection work on `feat/optical-photon-iteration1`, then port only that fix onto the multithreaded branch while preserving:

- multithreading;
- Hod2018/Hod2019 variants;
- TiO2/Vikuiti optical-surface differentiation;
- TTree branch names and structure;
- existing energy and timing scoring.

## Rule

Do not merge the full optical branch. Use manual cherry-pick of code fragments or a minimal edited patch only.
