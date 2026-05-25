# Angular resolution estimate

- Spatial estimator: `nph`
- Spatial region: `central`
- Method: parametric two-module propagation from single-module spatial resolutions.

Important: `D` is the internal X/Y plane separation inside one hodoscope module and must not be confused with `L`. `L` is the longitudinal distance between Hodo2018 and Hodo2019, measured between reconstructed active centers of the two complete modules.

This is not a replacement for a Geant4 simulation with two separated hodoscopes. It is a bridge quantity for connecting module characterization to Meiga/MuYSC acceptance and inversion studies.

| L [mm] | Pair | sigma theta x [mrad] | sigma theta y [mrad] | Method |
|---:|---|---:|---:|---|
| 50 | Hod2018/Vikuiti + Hod2019/TiO2 | 2.5305 | 8.33529 | two_module_parametric |
| 100 | Hod2018/Vikuiti + Hod2019/TiO2 | 1.26525 | 4.16764 | two_module_parametric |
| 200 | Hod2018/Vikuiti + Hod2019/TiO2 | 0.632624 | 2.08382 | two_module_parametric |
| 500 | Hod2018/Vikuiti + Hod2019/TiO2 | 0.25305 | 0.833529 | two_module_parametric |
| 1000 | Hod2018/Vikuiti + Hod2019/TiO2 | 0.126525 | 0.416764 | two_module_parametric |

σθ improves approximately as `1/L`. For production studies, MuYSC/Meiga should consume a two-module acceptance model or a full Geant4 telescope response when available.