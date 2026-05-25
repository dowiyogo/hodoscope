# HOD2018/HOD2019 instrument response summary

## 1. Branch, commit and date

- Branch: `test/optical-variant-16threads`
- Commit: `9ff1b37`
- Date: `2026-05-25T00:27:25`

## 2. Build and execution commands

```bash
rm -rf build
cmake -S . -B build
cmake --build build -j 16
HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac
HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac
python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 5 --dx 4 --dy 4
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_tio2.mac
HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_vikuiti.mac
python3.12 analysis/instrument_response/spatial_resolution_analysis.py
python3.12 analysis/instrument_response/virtual_pixel_efficiency.py --threshold-nph 1 --use nph
python3.12 analysis/instrument_response/angular_resolution_estimate.py
python3.12 analysis/instrument_response/accepted_muon_rate_estimate.py
python3.12 analysis/instrument_response/acceptance_matrix_builder.py
python3.12 analysis/instrument_response/threshold_sensitivity.py
python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 20 --dx 1 --dy 1
```

The executed position scan was the small validation scan (`dx=dy=4 mm`, `5` events per point). The production macros (`dx=dy=1 mm`, `20` events per point) were generated after the validation run but were not executed in this stage.

## 3. Physical configuration

- Hod2018 = Vikuiti ESR reflector
- Hod2019 = TiO2 optical epoxy paint reflector
- Scintillator = BC408 / EJ200-equivalent
- MPPC = S12572-100P label with ideal optical-photon collection volume

## 4. Optical result already validated

- TiO2 mean nph/event: `2.56`
- Vikuiti mean nph/event: `32.82`
- Vikuiti/TiO2 ratio: `12.8203`

## 5. Spatial resolution sigma_x, sigma_y

| Variant | sigma_x central nph [mm] | sigma_y central nph [mm] |
|---|---:|---:|
| Hod2019/TiO2 | 0.0778484 | 0.200715 |
| Hod2018/Vikuiti | 0.0997405 | 0.365248 |

## 6. Angular resolution estimate versus baseline L

`L` is the distance between active centers of Hodo2018 and Hodo2019, not the internal X/Y separation `D`.

| L [mm] | sigma_theta_x [mrad] | sigma_theta_y [mrad] |
|---:|---:|---:|
| 100 | 1.26525 | 4.16764 |
| 1000 | 0.126525 | 0.416764 |

## 7. Virtual pixel efficiency

- Mean pixel efficiency TiO2: `0.195062`
- Mean pixel efficiency Vikuiti: `0.782716`

## 8. Expected accepted muon rate

| Variant | Effective rate [arb.] | Efficiency |
|---|---:|---:|
| Hod2019/TiO2 | 0.000783499 | 0.392593 |
| Hod2018/Vikuiti | 0.001567 | 0.785185 |

## 9. Ideal versus effective acceptance

The acceptance tables separate a simplified geometric angular response from an effective response multiplied by the scan-derived efficiency. This is a pre-inversion angular response product, not the full voxelized `F` matrix.

## 10. Threshold sensitivity

| Variant | Threshold | Total efficiency | Relative counts |
|---|---:|---:|---:|
| Hod2019/TiO2 | 1 | 0.392593 | 1 |
| Hod2019/TiO2 | 2 | 0.195062 | 0.496855 |
| Hod2019/TiO2 | 5 | 0.0395062 | 0.100629 |
| Hod2019/TiO2 | 10 | 0.00740741 | 0.0188679 |
| Hod2019/TiO2 | 20 | 0 | 0 |
| Hod2019/TiO2 | 30 | 0 | 0 |
| Hod2018/Vikuiti | 1 | 0.785185 | 1 |
| Hod2018/Vikuiti | 2 | 0.782716 | 0.996855 |
| Hod2018/Vikuiti | 5 | 0.661728 | 0.842767 |
| Hod2018/Vikuiti | 10 | 0.37037 | 0.471698 |
| Hod2018/Vikuiti | 20 | 0.182716 | 0.232704 |
| Hod2018/Vikuiti | 30 | 0.0987654 | 0.125786 |

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
