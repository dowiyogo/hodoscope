# Iteration 1 optical validation summary

## Reflector-ratio diagnosis

The previous `nph = 0` issue was resolved before this diagnostic step. Optical photons are detected in the SiPM volumes, and the Hod2019/TiO2 and Hod2018/Vikuiti variants produce distinct `nph_NN` responses.

Physical quick-run result:

- TiO2 mean nph/event = 2.56
- Vikuiti mean nph/event = 32.82
- ratio Vikuiti/TiO2 = 12.8203125

Diagnostic reflector matrix:

- mode1 = TiO2 reflectivity + diffuse surface: mean nph/event = 2.56
- mode2 = ESR reflectivity + diffuse surface: mean nph/event = 32.158
- mode3 = TiO2 reflectivity + specular surface: mean nph/event = 2.44
- mode4 = ESR reflectivity + specular surface: mean nph/event = 32.432

Conclusion:

- The high factor is dominated by reflectivity, not by multithreading.
- The diffuse/specular angular change is not the main driver in the current test.
- The ratio is a model-dependent prediction and remains pending calibration.

Limitation:

The current ratio depends on simplified `R(lambda)`, idealized coupling, a simplified SiPM response, and the absence of direct calibration against Hod2018/Hod2019 data.
