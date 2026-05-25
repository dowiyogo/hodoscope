# Spatial resolution summary

## Method

This first-pass reconstruction uses the known bar-center geometry and a weighted centroid. Channels `00..15` reconstruct X, and channels `16..31` reconstruct Y. The same centroid is computed once using `edep_NN` weights and once using `nph_NN` weights.

Upper subplane centers are `-14,-10,-6,-2,2,6,10,14 mm`; lower subplanes are shifted by `+2 mm`. This matches the current single-module geometry and is not a two-module telescope fit.

The central region uses `|x| < 14 mm` and `|y| < 14 mm` to reduce edge effects from the scan boundary.

## Event-level signal checks

| Variant | Entries | Mean edep total [MeV] | Mean nph total | Mean active X/Y edep | Mean active X/Y nph |
|---|---:|---:|---:|---:|---:|
| Hod2019/TiO2 | 405 | 0.317791 | 4.84198 | 0.906173/0.918519 | 0.585185/0.590123 |
| Hod2018/Vikuiti | 405 | 0.313074 | 50.8099 | 0.898765/0.903704 | 0.891358/0.896296 |

## Resolution table

| Variant | Estimator | Coord | Region | Entries | Bias [mm] | Sigma [mm] | Robust sigma [mm] |
|---|---|---|---|---:|---:|---:|---:|
| Hod2019/TiO2 | edep | x | all | 360 | 0.0139443 | 0.197464 | 0.197464 |
| Hod2019/TiO2 | edep | x | central | 245 | 0.0219283 | 0.237891 | 0.237891 |
| Hod2019/TiO2 | edep | y | all | 361 | -0.0125144 | 0.229161 | 0.229161 |
| Hod2019/TiO2 | edep | y | central | 245 | -0.0282654 | 0.229254 | 0.229254 |
| Hod2019/TiO2 | nph | x | all | 236 | 0.00423729 | 0.0649564 | 0.0649564 |
| Hod2019/TiO2 | nph | x | central | 164 | 0.00609756 | 0.0778484 | 0.0778484 |
| Hod2019/TiO2 | nph | y | all | 235 | -0.015846 | 0.163524 | 0.163524 |
| Hod2019/TiO2 | nph | y | central | 152 | -0.0266917 | 0.200715 | 0.200715 |
| Hod2018/Vikuiti | edep | x | all | 360 | 0.00436655 | 0.0705982 | 0.0705982 |
| Hod2018/Vikuiti | edep | x | central | 245 | 0.00641616 | 0.0855011 | 0.0855011 |
| Hod2018/Vikuiti | edep | y | all | 360 | -0.0145584 | 0.294437 | 0.294437 |
| Hod2018/Vikuiti | edep | y | central | 245 | -0.021392 | 0.356707 | 0.356707 |
| Hod2018/Vikuiti | nph | x | all | 357 | 0.00319866 | 0.082318 | 0.082318 |
| Hod2018/Vikuiti | nph | x | central | 243 | 0.00469926 | 0.0997405 | 0.0997405 |
| Hod2018/Vikuiti | nph | y | all | 358 | -0.0122923 | 0.30227 | 0.30227 |
| Hod2018/Vikuiti | nph | y | central | 245 | -0.0179618 | 0.365248 | 0.365248 |

## Limitations

- This is a single-module centroid reconstruction, not a full track fit.
- The `nph` estimator uses ideal optical photons collected by the MPPC volume; it does not include PDE, electronics, dark noise, saturation, cross-talk, afterpulsing, or pulse shape.
- Angular resolution must be estimated parametrically until two complete hodoscopes are simulated together.
