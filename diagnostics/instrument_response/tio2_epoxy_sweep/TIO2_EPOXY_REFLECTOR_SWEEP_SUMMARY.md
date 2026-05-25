# TiO2+epoxy reflector sweep summary

This central-gun sweep varies an effective TiO2+optical-epoxy reflector model for Hod2019 without changing the default Hod2019/TiO2 behavior. The effective `R425` is a model knob near the EJ200 emission peak; it is not a measured material reflectivity.

The reported `estimated_npe_mean_pde30` is only an analysis estimate `0.30 * mean_total_nph`. It is not a ROOT branch, not a Geant4 PDE simulation, and not an electronics model.

| Model | R425 | Surface | Entries | Mean nph | Eff >=1 | Eff >=5 | Eff >=10 | Vikuiti/model | est. npe PDE30 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| TiO2 baseline |  | default | 500 | 2.56 | 0.466 | 0.002 | 0 | 12.6688 | 0.768 |
| TiO2+epoxy R425=0.930 diffuse | 0.93 | diffuse | 500 | 2.56 | 0.466 | 0.002 | 0 | 12.6688 | 0.768 |
| TiO2+epoxy R425=0.950 diffuse | 0.95 | diffuse | 500 | 9.3 | 0.964 | 0.202 | 0.008 | 3.48731 | 2.79 |
| TiO2+epoxy R425=0.952 diffuse | 0.952 | diffuse | 2000 | 12.1825 | 0.988 | 0.419 | 0.0115 | 2.66218 | 3.65475 |
| TiO2+epoxy R425=0.954 diffuse | 0.954 | diffuse | 2000 | 16.5825 | 0.9985 | 0.731 | 0.083 | 1.9558 | 4.97475 |
| TiO2+epoxy R425=0.956 diffuse | 0.956 | diffuse | 2000 | 25.4465 | 1 | 0.9645 | 0.486 | 1.27452 | 7.63395 |
| TiO2+epoxy R425=0.958 diffuse | 0.958 | diffuse | 2000 | 42.9235 | 1 | 1 | 0.9625 | 0.755577 | 12.877 |
| TiO2+epoxy R425=0.960 diffuse | 0.96 | diffuse | 2000 | 51.0595 | 1 | 1 | 0.9945 | 0.635181 | 15.3178 |
| TiO2+epoxy R425=0.962 diffuse | 0.962 | diffuse | 2000 | 62.9505 | 1 | 1 | 1 | 0.515198 | 18.8851 |
| TiO2+epoxy R425=0.964 diffuse | 0.964 | diffuse | 2000 | 81.7035 | 1 | 1 | 1 | 0.396947 | 24.5111 |
| TiO2+epoxy R425=0.966 diffuse | 0.966 | diffuse | 2000 | 114.338 | 1 | 1 | 1 | 0.283651 | 34.3013 |
| TiO2+epoxy R425=0.968 diffuse | 0.968 | diffuse | 2000 | 178.917 | 1 | 1 | 1 | 0.181268 | 53.6751 |
| TiO2+epoxy R425=0.970 diffuse | 0.97 | diffuse | 500 | 180.59 | 1 | 1 | 1 | 0.179589 | 54.177 |
| TiO2+epoxy R425=0.970 specular | 0.97 | specular | 500 | 182.46 | 1 | 1 | 1 | 0.177749 | 54.738 |
| TiO2+epoxy R425=0.980 diffuse | 0.98 | diffuse | 500 | 200.97 | 1 | 1 | 1 | 0.161377 | 60.291 |
| TiO2+epoxy R425=0.985 diffuse | 0.985 | diffuse | 500 | 216.076 | 1 | 1 | 1 | 0.150095 | 64.8228 |
| TiO2+epoxy R425=0.985 specular | 0.985 | specular | 500 | 216.902 | 1 | 1 | 1 | 0.149524 | 65.0706 |
| TiO2+epoxy R425=0.990 diffuse | 0.99 | diffuse | 500 | 248.068 | 1 | 1 | 1 | 0.130738 | 74.4204 |
| Vikuiti baseline |  | specular | 500 | 32.432 | 1 | 0.994 | 0.788 | 1 | 9.7296 |

## Interpretation

- Default TiO2 mean nph is `2.56`, while Vikuiti is `32.432`. In this central sweep the default model is lower than Vikuiti by a factor `12.6688`.
- Interpolated effective R425 for Vikuiti/model ratio near 10: `0.935813`.
- Interpolated effective R425 for ratio near 5: `0.946705`.
- Interpolated effective R425 for ratio near 3: `0.951181`.
- Interpolated effective R425 for ratio near 2: `0.953875`.
- First diffuse R425 with efficiency_nph_ge_1 > 0.90: `0.95`.
- First diffuse R425 with efficiency_nph_ge_5 > 0.50: `0.954`.
- First diffuse R425 with estimated_npe_mean_pde30 in 5..15: `0.956`.
- Closest sampled point to Vikuiti/model ratio 5: `R425=0.95` (mean nph `9.3`, Vikuiti/model `3.48731`, eff>=1 `0.964`, eff>=5 `0.202`, est. npe@30% `2.79`).
- Closest sampled point to ratio 3: `R425=0.952` (mean nph `12.1825`, Vikuiti/model `2.66218`, eff>=1 `0.988`, eff>=5 `0.419`, est. npe@30% `3.65475`).
- Closest sampled point to ratio 2: `R425=0.954` (mean nph `16.5825`, Vikuiti/model `1.9558`, eff>=1 `0.9985`, eff>=5 `0.731`, est. npe@30% `4.97475`).
- Sampled diffuse points with estimated_npe_mean_pde30 in 5..15: `R425=0.956`, `R425=0.958`.

## Recommendation

The fine sweep confirms a steep but now resolved transition between `R425=0.950` and `R425=0.958`. `R425=0.954 diffuse` is the best conservative position-scan candidate from the sampled points: it gives high `nph >= 1` efficiency, `nph >= 5` efficiency above 0.5, and keeps Hod2019 below the Vikuiti baseline.
Conservative candidate: `R425=0.954` (mean nph `16.5825`, Vikuiti/model `1.9558`, eff>=1 `0.9985`, eff>=5 `0.731`, est. npe@30% `4.97475`).
Upper sensitivity candidate: `R425=0.956` (mean nph `25.4465`, Vikuiti/model `1.27452`, eff>=1 `1`, eff>=5 `0.9645`, est. npe@30% `7.63395`).
For an intermediate spatial scan, use `dx=dy=2 mm` with `10` to `20` events per point before committing to another full `33 x 33` production scan.

## Limitations

- This is a central muon sweep, not a full position scan.
- Effective R425 is not a measured material constant.
- No `npe_NN`, PDE simulation, saturation, cross-talk, afterpulsing, noise, electronics, or pulse shape is implemented here.
- Surface-mode variations are sensitivity tests only.