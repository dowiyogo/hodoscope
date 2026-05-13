# Parameter sweep plan for optical reflector calibration

## Goal

Determine whether the high Vikuiti/TiO2 ratio can be explained by realistic effective reflectivities or whether the model needs geometric or surface refinements.

## Sweeps

### TiO2 reflectivity sweep

Suggested flat/effective values:

- 0.90
- 0.93
- 0.95
- 0.97
- 0.985
- 0.99

### ESR reflectivity sweep

Suggested flat/effective values:

- 0.970
- 0.980
- 0.985
- 0.990
- 0.995

### SigmaAlpha sweep

For TiO2:

- 0.02
- 0.05
- 0.10
- 0.20
- 0.30

For ESR:

- 0.00
- 0.01
- 0.02
- 0.05

### Bulk attenuation length sweep

If parametrized:

- 1 m
- 2.1 m
- 3 m
- 4 m

Note: BC-408 is reported with attenuation length around 210 cm in the hodoscope documentation.

### Geometry/coupling sweep

- improvedOptical on/off
- gap = 0 um
- gap = 10 um
- gap = 50 um
- gap = 100 um
- SiPM border surface on/off

## Metrics

For each configuration:

- mean nph/event
- median nph/event
- total nph
- events with nph > 0
- fraction events with nph > 0
- mean edep/event
- ratio Vikuiti/TiO2
- if implemented: number of boundary interactions per detected photon

## Acceptance criteria

Do not tune to force a specific ratio. The goal is to map sensitivity and identify whether the current large ratio is compatible with plausible optical parameters.
