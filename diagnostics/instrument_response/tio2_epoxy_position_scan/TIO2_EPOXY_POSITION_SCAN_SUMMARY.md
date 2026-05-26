# TiO2+epoxy position scan summary

## Intermediate scans

- Grid: `17 x 17`, `dx=dy=2 mm`
- Events per point: `20`
- Purpose: select a plausible TiO2+epoxy effective reflector candidate before a full scan.

| Model | Scan | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] | est. npe@30% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hod2019/TiO2 production | reference_production | 21780 | 7.02218 | 0.614555 | 0.0498163 | 0.657432 | 0.0366825 | 0.4942 | 0.4942 | 2.10665 |
| Hod2018/Vikuiti production | reference_production | 21780 | 77.897 | 0.935904 | 0.806382 | 0.996492 | 0.883472 | 0.114046 | 0.156063 | 23.3691 |
| TiO2+epoxy R425=0.954 diffuse intermediate | intermediate | 5780 | 26.7709 | 0.845156 | 0.421107 | 0.958444 | 0.487111 | 0.469286 | 0.671046 | 8.03128 |
| TiO2+epoxy R425=0.956 diffuse intermediate | intermediate | 5780 | 36.3042 | 0.881315 | 0.634429 | 0.995778 | 0.736889 | 0.333494 | 0.643959 | 10.8912 |

## Production scan

- Grid: `33 x 33`, `dx=dy=1 mm`
- Events per point: `20`
- Threads: `HODO_THREADS=16`
- Selected model: `R425=0.956 diffuse`, chosen because the intermediate scan improved threshold efficiency while staying below Vikuiti in mean nph.

| Model | Scan | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] | est. npe@30% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hod2019/TiO2 production | reference_production | 21780 | 7.02218 | 0.614555 | 0.0498163 | 0.657432 | 0.0366825 | 0.4942 | 0.4942 | 2.10665 |
| Hod2018/Vikuiti production | reference_production | 21780 | 77.897 | 0.935904 | 0.806382 | 0.996492 | 0.883472 | 0.114046 | 0.156063 | 23.3691 |
| TiO2+epoxy R425=0.956 diffuse production | production | 21780 | 54.1326 | 0.93719 | 0.792011 | 0.997681 | 0.862069 | 0.0823667 | 0.12355 | 16.2398 |

## Interpretation

- `R425=0.956 diffuse` production has `21780` entries, mean nph `54.1326`, and estimated npe@30% `16.2398`.
- Central efficiency is `0.997681` for `nph >= 1` and `0.862069` for `nph >= 5`.
- Spatial resolution estimate with the nph centroid is sigma_x `0.0823667 mm`, sigma_y `0.12355 mm`.
- `R425=0.956 diffuse` remains below the Vikuiti production mean nph and is far above the default TiO2 response, so it is a reasonable effective TiO2+epoxy production candidate.
- Do not run `R425=0.954 diffuse` production automatically from these results; keep it as a conservative systematic bracket for a later dedicated run.

## Limitations

- This is still an effective optical model. `R425` is not a measured physical reflectivity.
- `nph` is ideal MPPC-volume photon collection.
- No `npe_NN`, PDE, electronics, saturation, cross-talk, afterpulsing, dark noise, pulse shape, or final MuYSC/Meiga flux is included.
