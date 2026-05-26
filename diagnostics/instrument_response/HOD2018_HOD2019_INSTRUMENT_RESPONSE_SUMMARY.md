# HOD2018/HOD2019 instrument response summary

## 1. Branch, commit and date

- Branch: `test/optical-variant-16threads`
- Commit: `6be5f1f`
- Date: `2026-05-25T22:34:03`

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
python3.12 analysis/instrument_response/build_tio2_epoxy_sweep_macros.py --events 500 --r425-list "0.93,0.95,0.97,0.98,0.985,0.99" --surface-modes "diffuse"
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_tio2_baseline.mac
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_vikuiti_baseline.mac
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_tio2_epoxy_R425_0p950_diffuse.mac
python3.12 analysis/instrument_response/tio2_epoxy_sweep_analysis.py
python3.12 analysis/instrument_response/build_tio2_epoxy_position_scan_macros.py --r425-list "0.954,0.956" --events-per-point 20 --dx 2 --dy 2
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_position_scan/macros/position_scan_tio2_epoxy_R425_0p954_diffuse.mac
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_position_scan/macros/position_scan_tio2_epoxy_R425_0p956_diffuse.mac
python3.12 analysis/instrument_response/tio2_epoxy_position_scan_analysis.py
python3.12 analysis/instrument_response/build_instrument_response_summary.py
```

The current numbers in this report are from the production position scan unless a section explicitly says otherwise.

## Production scan configuration

- Branch: `test/optical-variant-16threads`
- Commit used for this report: `6be5f1f`
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
- Report generated at: `2026-05-25T22:34:03`

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

## TiO2+epoxy reflector sensitivity

Hod2019 experimentally corresponds to TiO2 plus optical epoxy paint, so the pure/default TiO2 surface model should be treated as a simplified effective model rather than a final material calibration. A central-gun sweep was run to test explicit TiO2+epoxy effective reflector overrides without changing the Hod2019 default.

- Default TiO2 central mean nph/event: `2.56`
- Vikuiti central mean nph/event: `32.432`
- Conservative TiO2+epoxy candidate: `R425=0.954 diffuse`, mean nph/event `16.5825`, efficiency nph>=1 `0.9985`, efficiency nph>=5 `0.731`
- Upper sensitivity candidate: `R425=0.956 diffuse`, mean nph/event `25.4465`, estimated npe@30% `7.63395`

| Model | R425 | Surface | Mean nph | Eff >=1 | Eff >=5 | Vikuiti/model |
|---|---:|---|---:|---:|---:|---:|
| TiO2 baseline |  | default | 2.56 | 0.466 | 0.002 | 12.6688 |
| TiO2+epoxy R425=0.930 diffuse | 0.93 | diffuse | 2.56 | 0.466 | 0.002 | 12.6688 |
| TiO2+epoxy R425=0.950 diffuse | 0.95 | diffuse | 9.3 | 0.964 | 0.202 | 3.48731 |
| TiO2+epoxy R425=0.952 diffuse | 0.952 | diffuse | 12.1825 | 0.988 | 0.419 | 2.66218 |
| TiO2+epoxy R425=0.954 diffuse | 0.954 | diffuse | 16.5825 | 0.9985 | 0.731 | 1.9558 |
| TiO2+epoxy R425=0.956 diffuse | 0.956 | diffuse | 25.4465 | 1 | 0.9645 | 1.27452 |
| TiO2+epoxy R425=0.958 diffuse | 0.958 | diffuse | 42.9235 | 1 | 1 | 0.755577 |
| TiO2+epoxy R425=0.960 diffuse | 0.96 | diffuse | 51.0595 | 1 | 1 | 0.635181 |
| TiO2+epoxy R425=0.962 diffuse | 0.962 | diffuse | 62.9505 | 1 | 1 | 0.515198 |
| TiO2+epoxy R425=0.964 diffuse | 0.964 | diffuse | 81.7035 | 1 | 1 | 0.396947 |
| TiO2+epoxy R425=0.966 diffuse | 0.966 | diffuse | 114.338 | 1 | 1 | 0.283651 |
| TiO2+epoxy R425=0.968 diffuse | 0.968 | diffuse | 178.917 | 1 | 1 | 0.181268 |
| TiO2+epoxy R425=0.970 diffuse | 0.97 | diffuse | 180.59 | 1 | 1 | 0.179589 |
| TiO2+epoxy R425=0.980 diffuse | 0.98 | diffuse | 200.97 | 1 | 1 | 0.161377 |
| TiO2+epoxy R425=0.985 diffuse | 0.985 | diffuse | 216.076 | 1 | 1 | 0.150095 |
| TiO2+epoxy R425=0.990 diffuse | 0.99 | diffuse | 248.068 | 1 | 1 | 0.130738 |
| Vikuiti baseline |  | specular | 32.432 | 1 | 0.994 | 1 |

The fine sweep resolves the steep transition: `R425=0.954 diffuse` is close to Vikuiti/model ratio 2, while `R425=0.956 diffuse` enters the 5..15 analysis-only estimated npe@30% range. A good next step is an intermediate position scan with `dx=dy=2 mm` and `10` to `20` events per point for `R425=0.954 diffuse`; optionally add `R425=0.956 diffuse` as the upper sensitivity case.

This `R425` is an effective model reflectivity near 425 nm, not a measured physical reflectivity of the TiO2+epoxy mixture. It still needs calibration against experimental data.

## TiO2+epoxy production candidate

Intermediate and production scans were run for effective TiO2+epoxy reflector candidates selected by the central sweep. `R425=0.956 diffuse` was chosen for production because it improved threshold efficiency in the intermediate scan while staying below the Vikuiti production mean nph.

- Intermediate scans available: `2`
- Production scans available: `1`
- Production candidate configuration: `R425=0.956 diffuse`, `dx=dy=1 mm`, `33 x 33`, `20` events per point, `HODO_THREADS=16`

| Model | Scan | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] | est. npe@30% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TiO2+epoxy R425=0.954 diffuse intermediate | intermediate | 5780 | 26.7709 | 0.845156 | 0.421107 | 0.958444 | 0.487111 | 0.469286 | 0.671046 | 8.03128 |
| TiO2+epoxy R425=0.956 diffuse intermediate | intermediate | 5780 | 36.3042 | 0.881315 | 0.634429 | 0.995778 | 0.736889 | 0.333494 | 0.643959 | 10.8912 |
| TiO2+epoxy R425=0.956 diffuse production | production | 21780 | 54.1326 | 0.93719 | 0.792011 | 0.997681 | 0.862069 | 0.0823667 | 0.12355 | 16.2398 |

`R425=0.956 diffuse` production entries: `21780`.
`R425=0.956 diffuse` remains the production candidate. `R425=0.954 diffuse` should stay as a conservative systematic bracket for a later run rather than being run automatically here.

The `R425` values are effective model reflectivities near 425 nm, not measured material reflectivities.

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
