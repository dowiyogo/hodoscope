# TiO2+epoxy intermediate position scan summary

## Configuration

- Detector variant: `Hod2019`
- Reflector model: TiO2+epoxy effective, `diffuse` surface mode
- R425 values: `0.954`, `0.956`
- Grid: `x,y = -16,-14,...,+16 mm`
- Step: `dx=dy=2 mm`
- Events per point: `20`
- Expected events per model: `5780`
- Threads: `HODO_THREADS=16`

## Summary table

| Model | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Hod2019/TiO2 production | 21780 | 7.02218 | 0.614555 | 0.0498163 | 0.657432 | 0.0366825 | 0.4942 | 0.4942 |
| Hod2018/Vikuiti production | 21780 | 77.897 | 0.935904 | 0.806382 | 0.996492 | 0.883472 | 0.114046 | 0.156063 |
| TiO2+epoxy R425=0.954 diffuse | 5780 | 26.7709 | 0.845156 | 0.421107 | 0.958444 | 0.487111 | 0.469286 | 0.671046 |
| TiO2+epoxy R425=0.956 diffuse | 5780 | 36.3042 | 0.881315 | 0.634429 | 0.995778 | 0.736889 | 0.333494 | 0.643959 |

## Interpretation

- `R425=0.954 diffuse` has high central `nph >= 1` efficiency and remains well below the Vikuiti production mean nph, making it the conservative model.
- `R425=0.956 diffuse` improves the `nph >= 5` efficiency and spatial response, remains below the Vikuiti production mean nph, and does not look like an absurd overcorrection in this intermediate scan.
- Recommendation: `R425=0.954 diffuse` is the conservative candidate, but `R425=0.956 diffuse` is the stronger single production candidate in this intermediate scan because it improves threshold efficiency and spatial response while staying below the Vikuiti production mean nph.
- For the next production position scan, run both `0.954` and `0.956` if time permits. If only one production scan is practical, run `R425=0.956 diffuse`; keep `0.954` as the conservative systematic bracket.

## Limitations

- This is an intermediate `17 x 17` position scan, not the full `33 x 33` production scan.
- `R425` is an effective model reflectivity near 425 nm, not a measured physical reflectivity.
- `nph` is ideal MPPC-volume photon collection; no `npe_NN`, PDE, electronics, saturation, cross-talk, afterpulsing, dark noise, or pulse shape is included.
