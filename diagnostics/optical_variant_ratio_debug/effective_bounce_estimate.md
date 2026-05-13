# Effective bounce estimate

## Approximation

Use the simplified survival model:

```text
ratio ~= (R_ESR / R_TiO2)^N_eff
```

Solving for the effective number of reflections:

```text
N_eff ~= ln(ratio) / ln(R_ESR / R_TiO2)
```

This is not a measurement of the actual Geant4 boundary count. It is an order-of-magnitude estimate of how many effective reflectivity-weighted interactions would be needed to produce the observed ratio.

## Inputs

Observed ratio:

```text
ratio Vikuiti/TiO2 = 12.82
```

## Scenarios

| Scenario | R_ESR | R_TiO2 | ratio | N_eff |
|---|---:|---:|---:|---:|
| A | 0.990 | 0.970 | 12.82 | 124.995 |
| B | 0.985 | 0.930 | 12.82 | 44.398 |
| C | 0.990 | 0.930 | 12.82 | 40.803 |
| D | 0.985 | 0.960 | 12.82 | 99.229 |

## Interpretation

The inferred `N_eff` is very sensitive to which effective reflectivity values are used. Around the EJ-200 emission peak, using `R_ESR = 0.985` and `R_TiO2 = 0.930` gives `N_eff ~= 44`. Using the higher TiO2 value `R_TiO2 = 0.970` gives `N_eff ~= 125`.

If the real photon paths involve tens of effective boundary interactions before reaching the SiPM, a large Vikuiti/TiO2 ratio can be a natural consequence of the current surface model. If the true effective bounce count should be much smaller, then the model needs further checks of boundary handling, absorption, coupling geometry, and reflectivity assumptions.

## Consequence

The ratio is extremely sensitive to `R(lambda)`. A calibration or uncertainty study should treat the reflector reflectivity as one of the dominant optical parameters.
