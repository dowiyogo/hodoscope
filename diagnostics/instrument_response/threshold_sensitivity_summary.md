# Threshold sensitivity summary

This scan evaluates how a simple per-channel `nph` threshold changes detection efficiency, effective acceptance, and relative expected counts.

| Variant | Threshold | Total eff. | Central eff. | Relative counts | Relative Poisson weight |
|---|---:|---:|---:|---:|---:|
| Hod2019/TiO2 | 1 | 0.614555 | 0.657432 | 1 | 1 |
| Hod2019/TiO2 | 2 | 0.338705 | 0.346492 | 0.551139 | 1.81442 |
| Hod2019/TiO2 | 5 | 0.0498163 | 0.0366825 | 0.0810609 | 12.3364 |
| Hod2019/TiO2 | 10 | 0.00238751 | 0.00112961 | 0.00388495 | 257.404 |
| Hod2019/TiO2 | 20 | 4.59137e-05 | 0 | 7.47105e-05 | 13385 |
| Hod2019/TiO2 | 30 | 0 | 0 | 0 | inf |
| Hod2018/Vikuiti | 1 | 0.935904 | 0.996492 | 1 | 1 |
| Hod2018/Vikuiti | 2 | 0.920202 | 0.984899 | 0.983222 | 1.01706 |
| Hod2018/Vikuiti | 5 | 0.806382 | 0.883472 | 0.861607 | 1.16062 |
| Hod2018/Vikuiti | 10 | 0.625207 | 0.683532 | 0.668024 | 1.49695 |
| Hod2018/Vikuiti | 20 | 0.370156 | 0.387872 | 0.395506 | 2.5284 |
| Hod2018/Vikuiti | 30 | 0.19123 | 0.18365 | 0.204327 | 4.89412 |

Higher thresholds reduce acceptance and therefore reduce expected counts. In an inversion, this changes Poisson statistical weights approximately as `W proportional to 1 / expected_counts`; bins with lower efficiency need explicit response modeling rather than silent normalization.

The Vikuiti/ESR variant retains efficiency to higher thresholds because its ideal MPPC-volume photon collection is much larger in the current optical model.