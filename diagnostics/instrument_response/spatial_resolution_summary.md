# Spatial resolution summary

## Method

This first-pass reconstruction uses the known bar-center geometry and a weighted centroid. Channels `00..15` reconstruct X, and channels `16..31` reconstruct Y. The same centroid is computed once using `edep_NN` weights and once using `nph_NN` weights.

Upper subplane centers are `-14,-10,-6,-2,2,6,10,14 mm`; lower subplanes are shifted by `+2 mm`. This matches the current single-module geometry and is not a two-module telescope fit.

The central region uses `|x| < 14 mm` and `|y| < 14 mm` to reduce edge effects from the scan boundary.

## Event-level signal checks

| Variant | Entries | Mean edep total [MeV] | Mean nph total | Mean active X/Y edep | Mean active X/Y nph |
|---|---:|---:|---:|---:|---:|
| Hod2019/TiO2 | 21780 | 0.521737 | 7.02218 | 1.44568/1.468 | 0.970707/0.987741 |
| Hod2018/Vikuiti | 21780 | 0.521231 | 77.897 | 1.44619/1.47011 | 1.43632/1.459 |

## Resolution table

| Variant | Estimator | Coord | Region | Entries | Bias [mm] | Sigma [mm] | Robust sigma [mm] |
|---|---|---|---|---:|---:|---:|---:|
| Hod2019/TiO2 | edep | x | all | 21121 | 0.0304088 | 0.381777 | 0.00442347 |
| Hod2019/TiO2 | edep | x | central | 14580 | 0.00226419 | 0.343172 | 0.0118396 |
| Hod2019/TiO2 | edep | y | all | 21128 | 0.0339014 | 0.594664 | 0.00905263 |
| Hod2019/TiO2 | edep | y | central | 14580 | 0.00260419 | 0.56787 | 0.01839 |
| Hod2019/TiO2 | nph | x | all | 17089 | 0.0337719 | 0.786796 | 0.4942 |
| Hod2019/TiO2 | nph | x | central | 11963 | 0.00956482 | 0.794218 | 0.4942 |
| Hod2019/TiO2 | nph | y | all | 17088 | 0.0249581 | 0.973345 | 0.4942 |
| Hod2019/TiO2 | nph | y | central | 11948 | 0.000280908 | 0.973997 | 0.4942 |
| Hod2018/Vikuiti | edep | x | all | 21123 | 0.0336332 | 0.367516 | 0.00441828 |
| Hod2018/Vikuiti | edep | x | central | 14580 | 0.00333945 | 0.321331 | 0.0130622 |
| Hod2018/Vikuiti | edep | y | all | 21129 | 0.0340519 | 0.552085 | 0.00901396 |
| Hod2018/Vikuiti | edep | y | central | 14580 | 0.00305648 | 0.528557 | 0.0177353 |
| Hod2018/Vikuiti | nph | x | all | 21060 | 0.0352702 | 0.642171 | 0.0511241 |
| Hod2018/Vikuiti | nph | x | central | 14564 | 0.00737823 | 0.591001 | 0.114046 |
| Hod2018/Vikuiti | nph | y | all | 21072 | 0.0319213 | 0.762518 | 0.1059 |
| Hod2018/Vikuiti | nph | y | central | 14560 | 0.00279925 | 0.741063 | 0.156063 |

## Limitations

- This is a single-module centroid reconstruction, not a full track fit.
- The `nph` estimator uses ideal optical photons collected by the MPPC volume; it does not include PDE, electronics, dark noise, saturation, cross-talk, afterpulsing, or pulse shape.
- Angular resolution must be estimated parametrically until two complete hodoscopes are simulated together.
