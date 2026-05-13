# Final interpretation: TiO2 vs Vikuiti optical response

## Status

- The previous `nph = 0` bug has already been resolved in `feat/multithreading`.
- Optical photon detection in the SiPM volumes is working.
- ST and MT produce the same ratio in the test performed.
- The Hod2019/TiO2 and Hod2018/Vikuiti detector variants are observable through the `nph_NN` branches.

## Numerical result

- TiO2 mean nph/event = 2.56
- Vikuiti mean nph/event = 32.82
- ratio Vikuiti/TiO2 = 12.8203125

Diagnostic matrix:

| Mode | Reflectivity set | Angular model | mean nph/event |
|---|---|---|---:|
| mode1 | TiO2 | diffuse | 2.56 |
| mode2 | ESR | diffuse | 32.158 |
| mode3 | TiO2 | specular | 2.44 |
| mode4 | ESR | specular | 32.432 |

Ratios:

- mode2/mode1 = 12.56171875, approximately 12.56
- mode3/mode1 = 0.953125, approximately 0.95
- mode4/mode3 = 13.29180328, approximately 13.29
- mode4/mode1 = 12.66875, approximately 12.67

## Main conclusion

The large Vikuiti/TiO2 ratio is not caused by multithreading and is not mainly caused by diffuse-vs-specular angular transport in the current test. It is dominated by the reflectivity curve assigned to the reflector. The effect is amplified by the large number of optical boundary interactions before photons reach the SiPM.

La razon alta Vikuiti/TiO2 no proviene de MT ni principalmente del cambio difuso/especular en esta prueba. Esta dominada por la reflectividad asignada al reflector y por la supervivencia acumulada tras muchos rebotes.

## Physical interpretation

In a thin, long scintillator bar, optical photons can bounce many times before reaching the SiPM. The accumulated survival probability scales approximately as `R^N`, where `R` is the effective reflectivity and `N` is the effective number of boundary interactions.

For that reason, an apparently moderate difference in `R(lambda)` can produce a large difference in detected `nph` if `N` is large. In the current model, replacing `R_TiO2` with `R_ESR` reproduces almost the full observed factor. The diffuse/specular angular change has a small effect in the tested configuration.

## Why this is not currently treated as a bug

- `nph` is nonzero for both variants.
- ST and MT give the same ratio.
- The same `SiPMSD` code counts photons for both variants.
- The 2x2 matrix separated reflectivity and angularity.
- The large factor appears when only reflectivity is changed.
- There is no evidence of a TTree failure or SiPMSD counting failure.

## Important caveat

This does not mean that the experimental detector must have a Vikuiti/TiO2 ratio of 12.8. It means that, given the current Geant4 optical parameters and surface model, the simulated detector predicts a large reflectivity-dominated enhancement.

Esto no significa que el detector experimental deba tener una razon Vikuiti/TiO2 de 12.8. Significa que, dados los parametros opticos y el modelo de superficies actuales en Geant4, la simulacion predice un realce grande dominado por reflectividad.

## Limitations

- The spectral reflectivities are simplified.
- Only four photon-energy points are used.
- `R(lambda)` has not been calibrated with local measurements.
- Physical reflector and Kapton volumes are not modeled.
- The effective number of bounces has not been measured directly.
- The SiPM PDE model is simplified.
- The optical coupling is idealized.
- There is no direct comparison to Hod2018/Hod2019 data yet.
- The TiO2 model may be penalized if the effective reflectivity used here is too low for the real geometry.
- The ESR model may be idealized if the effective reflectivity used here is too high.

## Recommended next steps

1. Measure or estimate the effective number of bounces per detected photon.
2. Sweep `R_TiO2` and `R_ESR`.
3. Sweep scintillator bulk absorption.
4. Sweep attenuation length.
5. Separate detected photons by longitudinal distance to the SiPM.
6. Compare against experimental data if available.
7. Calibrate reflectivities or roughness only after the sensitivity studies.
