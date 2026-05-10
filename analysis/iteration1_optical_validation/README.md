# Iteration 1 — Optical minimal validation

This folder contains a minimal validation suite for Iteration 1 (optical
transport minimal). It verifies that enabling optical physics preserves
the Iteration 0 behaviour when optics are disabled and provides a
diagnostic path for optical transport.

Activate optics via environment variable:

```
export HODO_ENABLE_OPTICAL=1
```

Run the validation with:

```
bash run_iteration1_optical_validation.sh
```

Limitations:
- No PDE, dark counts, afterpulsing, crosstalk or digitization are applied.
- Optical properties are approximate and for transport testing only.
- Optical photon detection is not yet validated; current runs show `nph = 0`.

See `ITERATION1_OPTICAL_VALIDATION_SUMMARY.md` for results.
