# Threshold sensitivity summary

This scan evaluates how a simple per-channel `nph` threshold changes detection efficiency, effective acceptance, and relative expected counts.

| Variant | Threshold | Total eff. | Central eff. | Relative counts | Relative Poisson weight |
|---|---:|---:|---:|---:|---:|
| Hod2019/TiO2 | 1 | 0.392593 | 0.416327 | 1 | 1 |
| Hod2019/TiO2 | 2 | 0.195062 | 0.159184 | 0.496855 | 2.01266 |
| Hod2019/TiO2 | 5 | 0.0395062 | 0.0163265 | 0.100629 | 9.9375 |
| Hod2019/TiO2 | 10 | 0.00740741 | 0 | 0.0188679 | 53 |
| Hod2019/TiO2 | 20 | 0 | 0 | 0 | inf |
| Hod2019/TiO2 | 30 | 0 | 0 | 0 | inf |
| Hod2018/Vikuiti | 1 | 0.785185 | 0.991837 | 1 | 1 |
| Hod2018/Vikuiti | 2 | 0.782716 | 0.987755 | 0.996855 | 1.00315 |
| Hod2018/Vikuiti | 5 | 0.661728 | 0.812245 | 0.842767 | 1.18657 |
| Hod2018/Vikuiti | 10 | 0.37037 | 0.404082 | 0.471698 | 2.12 |
| Hod2018/Vikuiti | 20 | 0.182716 | 0.159184 | 0.232704 | 4.2973 |
| Hod2018/Vikuiti | 30 | 0.0987654 | 0.0816327 | 0.125786 | 7.95 |

Higher thresholds reduce acceptance and therefore reduce expected counts. In an inversion, this changes Poisson statistical weights approximately as `W proportional to 1 / expected_counts`; bins with lower efficiency need explicit response modeling rather than silent normalization.

The Vikuiti/ESR variant retains efficiency to higher thresholds because its ideal MPPC-volume photon collection is much larger in the current optical model.