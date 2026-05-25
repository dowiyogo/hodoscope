# HOD2018/HOD2019 instrument response summary

## 1. Branch, commit and date

- Branch: `test/optical-variant-16threads`
- Commit: `31b3cf0`
- Date: `2026-05-25T01:55:57`

## 2. Build and execution commands

```bash
rm -rf build
cmake -S . -B build
cmake --build build -j 16
python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 20 --dx 1 --dy 1
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_tio2.mac
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_vikuiti.mac
python3.12 analysis/instrument_response/spatial_resolution_analysis.py
python3.12 analysis/instrument_response/virtual_pixel_efficiency.py --threshold-nph 1 --use nph
python3.12 analysis/instrument_response/angular_resolution_estimate.py
python3.12 analysis/instrument_response/accepted_muon_rate_estimate.py
python3.12 analysis/instrument_response/acceptance_matrix_builder.py
python3.12 analysis/instrument_response/threshold_sensitivity.py
python3.12 analysis/instrument_response/build_instrument_response_summary.py
```

The current numbers in this report are from the production position scan unless a section explicitly says otherwise.

## Production scan configuration

- Branch: `test/optical-variant-16threads`
- Commit used for this report: `31b3cf0`
- Threads: `HODO_THREADS=16`
- Grid: `33 x 33` positions
- Range: `x,y = -16 mm ... +16 mm`
- Step: `dx=dy=1 mm`
- Events per point: `20`
- Expected events per variant: `21780`
- TiO2 actual events: `21780`
- Vikuiti actual events: `21780`
- TiO2 ROOT: `diagnostics/instrument_response/outputs/position_scan_tio2.root`
- Vikuiti ROOT: `diagnostics/instrument_response/outputs/position_scan_vikuiti.root`
- TiO2 scan exit/duration: `0`, `1008 s`
- Vikuiti scan exit/duration: `0`, `3179 s`
- Report generated at: `2026-05-25T01:55:57`

## Small scan vs production scan

The previous validation pass used `dx=dy=4 mm` with `5` events per point. That small scan validated the full analysis chain and exposed threshold semantics, but it is not the source of the current instrument-response numbers. The current tables and summaries use the production scan with `dx=dy=1 mm` and `20` events per point.

## 3. Physical configuration

- Hod2018 = Vikuiti ESR reflector
- Hod2019 = TiO2 optical epoxy paint reflector
- Scintillator = BC408 / EJ200-equivalent
- MPPC = S12572-100P label with ideal optical-photon collection volume

## 4. Optical signal

Production position-scan mean total `nph/event`:

- TiO2: `7.02218`
- Vikuiti: `77.897`
- Vikuiti/TiO2 ratio: `11.093`

Earlier quick optical validation at the central gun position:

- TiO2 mean nph/event: `2.56`
- Vikuiti mean nph/event: `32.82`
- Vikuiti/TiO2 ratio: `12.8203`

## 5. Spatial resolution sigma_x, sigma_y

| Variant | sigma_x central nph [mm] | sigma_y central nph [mm] |
|---|---:|---:|
| Hod2019/TiO2 | 0.4942 | 0.4942 |
| Hod2018/Vikuiti | 0.114046 | 0.156063 |

## 6. Angular resolution estimate versus baseline L

`L` is the distance between active centers of Hodo2018 and Hodo2019, not the internal X/Y separation `D`.

| L [mm] | sigma_theta_x [mrad] | sigma_theta_y [mrad] |
|---:|---:|---:|
| 100 | 5.07188 | 5.18256 |
| 1000 | 0.507188 | 0.518256 |

## 7. Virtual pixel efficiency

- Mean pixel efficiency TiO2: `0.614555`
- Mean pixel efficiency Vikuiti: `0.935904`

## 8. Expected accepted muon rate

| Variant | Effective rate [arb.] | Efficiency |
|---|---:|---:|
| Hod2019/TiO2 | 0.00122647 | 0.614555 |
| Hod2018/Vikuiti | 0.00186779 | 0.935904 |

## 9. Ideal versus effective acceptance

The acceptance tables separate a simplified geometric angular response from an effective response multiplied by the scan-derived efficiency. This is a pre-inversion angular response product, not the full voxelized `F` matrix.

## 10. Threshold sensitivity

| Variant | Threshold | Total efficiency | Relative counts |
|---|---:|---:|---:|
| Hod2019/TiO2 | 1 | 0.614555 | 1 |
| Hod2019/TiO2 | 2 | 0.338705 | 0.551139 |
| Hod2019/TiO2 | 5 | 0.0498163 | 0.0810609 |
| Hod2019/TiO2 | 10 | 0.00238751 | 0.00388495 |
| Hod2019/TiO2 | 20 | 4.59137e-05 | 7.47105e-05 |
| Hod2019/TiO2 | 30 | 0 | 0 |
| Hod2018/Vikuiti | 1 | 0.935904 | 1 |
| Hod2018/Vikuiti | 2 | 0.920202 | 0.983222 |
| Hod2018/Vikuiti | 5 | 0.806382 | 0.861607 |
| Hod2018/Vikuiti | 10 | 0.625207 | 0.668024 |
| Hod2018/Vikuiti | 20 | 0.370156 | 0.395506 |
| Hod2018/Vikuiti | 30 | 0.19123 | 0.204327 |

## 11. Connection to the abstract

These outputs connect Geant4 module response (`edep`, `nph`, efficiency and acceptance) to the muography chain expected by Meiga/MuYSC: angular flux and acceptance can be folded into expected counts, while threshold-dependent efficiencies can enter inversion weights.

## 12. Limitations

- `nph` does not include real PDE.
- No pulse simulation or electronics response is included.
- No saturation, cross-talk, afterpulsing, or dark noise is included.
- Real flux must come from MuYSC/Meiga for production.
- The current geometry is a single hodoscope module; sigma_theta is parametric until two modules are simulated together.

## 13. Recommended next step

Add `npe_NN` with S12572-100P PDE and a configurable threshold model, then connect either a MuYSC angular flux table or a two-module Geant4 geometry to replace the parametric angular response.
