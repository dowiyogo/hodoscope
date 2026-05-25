# Angular resolution estimate

- Spatial estimator: `nph`
- Spatial region: `central`
- Method: parametric two-module propagation from single-module spatial resolutions.

Important: `D` is the internal X/Y plane separation inside one hodoscope module and must not be confused with `L`. `L` is the longitudinal distance between Hodo2018 and Hodo2019, measured between reconstructed active centers of the two complete modules.

This is not a replacement for a Geant4 simulation with two separated hodoscopes. It is a bridge quantity for connecting module characterization to Meiga/MuYSC acceptance and inversion studies.

| L [mm] | Pair | sigma theta x [mrad] | sigma theta y [mrad] | Method |
|---:|---|---:|---:|---|
| 50 | Hod2018/Vikuiti + Hod2019/TiO2 | 10.1438 | 10.3651 | two_module_parametric |
| 100 | Hod2018/Vikuiti + Hod2019/TiO2 | 5.07188 | 5.18256 | two_module_parametric |
| 200 | Hod2018/Vikuiti + Hod2019/TiO2 | 2.53594 | 2.59128 | two_module_parametric |
| 500 | Hod2018/Vikuiti + Hod2019/TiO2 | 1.01438 | 1.03651 | two_module_parametric |
| 1000 | Hod2018/Vikuiti + Hod2019/TiO2 | 0.507188 | 0.518256 | two_module_parametric |

σθ improves approximately as `1/L`. For production studies, MuYSC/Meiga should consume a two-module acceptance model or a full Geant4 telescope response when available.