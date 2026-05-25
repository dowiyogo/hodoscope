# Acceptance matrix summary

The ideal matrix contains a simplified angular geometric acceptance proportional to `cos(theta) dOmega`. The effective matrices multiply the ideal term by the scan-derived detection efficiency for each detector variant and threshold.

- theta bins: `12`
- phi bins: `24`
- theta max: `60.0 deg`
- threshold nph: `1.0`

| Variant | Efficiency applied |
|---|---:|
| Hod2019/TiO2 | 0.392593 |
| Hod2018/Vikuiti | 0.785185 |

This is not yet the voxelized inversion matrix `F`. It is an angular response product that can be consumed by later Meiga/MuYSC coupling to build `F` with realistic flux, geometry, and material paths.