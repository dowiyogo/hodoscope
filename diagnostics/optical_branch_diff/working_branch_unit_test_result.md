# Unit optical test result

Date: 2026-05-12

Command:

```bash
HODO_ENABLE_OPTICAL=1 ./build/optical_unit_test test_optical/macros/unit_test_optical.mac
```

Final counters from `logs/unit_run.log`:

```text
n_photons_generated: 172809
n_photons_absorbed_in_scint: 1181
n_photons_killed_at_paint: 159146
n_photons_crossed_to_air: 2534112
n_photons_entered_sipm: 14040
n_photons_detected: 14040
detected_over_generated: 0.0812458
```

Minimum step-3 criteria:

- `n_photons_generated > 0`: pass
- `n_photons_entered_sipm > 0`: pass
- `n_photons_detected > 0`: pass

Step-5 efficiency criterion:

- `n_photons_detected / n_photons_generated = 0.0812458`: pass
- Required floor: `> 0.05`

Observed case:

The final unit test is not production-limited and not SD-limited. Scintillation produces optical photons, photons reach the SiPM volume, and the SiPM counting path observes them. The failing intermediate configurations were transport/coupling limited.
