# TiO2+epoxy reflector sweep summary

This central-gun sweep varies an effective TiO2+optical-epoxy reflector model for Hod2019 without changing the default Hod2019/TiO2 behavior. The effective `R425` is a model knob near the EJ200 emission peak; it is not a measured material reflectivity.

The reported `estimated_npe_mean_pde30` is only an analysis estimate `0.30 * mean_total_nph`. It is not a ROOT branch, not a Geant4 PDE simulation, and not an electronics model.

| Model | R425 | Surface | Entries | Mean nph | Eff >=1 | Eff >=5 | Eff >=10 | Vikuiti/model | est. npe PDE30 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| TiO2 baseline |  | default | 500 | 2.56 | 0.466 | 0.002 | 0 | 12.6688 | 0.768 |
| TiO2+epoxy R425=0.930 diffuse | 0.93 | diffuse | 500 | 2.56 | 0.466 | 0.002 | 0 | 12.6688 | 0.768 |
| TiO2+epoxy R425=0.950 diffuse | 0.95 | diffuse | 500 | 9.3 | 0.964 | 0.202 | 0.008 | 3.48731 | 2.79 |
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
- Interpolated effective R425 for ratio near 3: `0.952947`.
- Interpolated effective R425 for ratio near 2: `0.958993`.
- First diffuse R425 with efficiency_nph_ge_1 > 0.90: `0.95`.
- First diffuse R425 with efficiency_nph_ge_5 > 0.50: `0.97`.
- First diffuse R425 with estimated_npe_mean_pde30 in 5..15: `not reached`.

## Recommendation

The response changes steeply between `R425=0.950` and `R425=0.970`. `R425=0.950 diffuse` is the best conservative candidate from this coarse sweep: it gives high `nph >= 1` efficiency without forcing Hod2019 to exceed the Vikuiti baseline.
`R425=0.950 diffuse` has mean nph `9.3`, efficiency_nph_ge_1 `0.964`, and Vikuiti/model ratio `3.48731`.
`R425=0.970 diffuse` is an aggressive upper sensitivity point: mean nph `180.59` and Vikuiti/model ratio `0.179589`.
Before a long spatial scan, run a finer central sweep around `R425=0.955,0.960,0.965`. If only one immediate spatial candidate is needed, use `R425=0.950 diffuse`; if two are needed, pair it with one finer-grid point near the interpolated ratio target rather than jumping directly to `0.970`.

## Limitations

- This is a central muon sweep, not a full position scan.
- Effective R425 is not a measured material constant.
- No `npe_NN`, PDE simulation, saturation, cross-talk, afterpulsing, noise, electronics, or pulse shape is implemented here.
- Surface-mode variations are sensitivity tests only.