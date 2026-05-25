# Virtual pixel efficiency summary

- Detection observable: `nph`
- Per-channel threshold: `1.0`
- Event is detected when at least one X channel and at least one Y channel are active.

| Variant | Total efficiency | Central 29x29 mm2 efficiency | Min pixel eff. | Max pixel eff. | Mean nph total |
|---|---:|---:|---:|---:|---:|
| Hod2019/TiO2 | 0.392593 | 0.416327 | 0 | 1 | 4.84198 |
| Hod2018/Vikuiti | 0.785185 | 0.991837 | 0 | 1 | 50.8099 |

## Low-efficiency pixels

Pixels with low efficiency are expected near edges and at threshold values where the idealized optical collection is sparse. These tables are a first format for later acceptance weighting in Meiga/MuYSC workflows.

## Limitations

- Uses a scan-generated event sample, not a cosmic angular distribution.
- `nph` is ideal MPPC-volume photon collection and has no real PDE or electronics response yet.