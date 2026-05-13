# Model recommendation

## Diagnosis

The large Vikuiti/TiO2 ratio is dominated by the reflector reflectivity spectrum under repeated reflections.

The key controlled comparisons are:

- `mode2/mode1 = 12.56171875`: same diffuse surface, ESR reflectivity instead of TiO2 reflectivity.
- `mode3/mode1 = 0.953125`: same TiO2 reflectivity, specular surface instead of diffuse surface.
- `mode4/mode3 = 13.29180328`: same specular surface, ESR reflectivity instead of TiO2 reflectivity.

This means the simplified model is very sensitive to `R(lambda)` because photons undergo enough bounces that the survival probability behaves roughly like `R^N`.

## Recommendation

Do not tune the reflectivity arrays to force the preliminary target ratio.

For the next physical iteration:

1. Add a boundary-status diagnostic stepping action behind a flag to count `Absorption`, `Detection`, `LambertianReflection`, `SpikeReflection`, `TotalInternalReflection`, `FresnelReflection`, `NoRINDEX`, and `StepTooSmall`.
2. Run a longitudinal source-position scan to estimate the effective number of bounces and compare it with simple optical-guide expectations.
3. Split the simplified reflector model into explicit studies of `type`, `finish`, `sigmaAlpha`, and `R(lambda)` using more than the current 2x2 modes.
4. Consider a more physical SiPM coupling model with explicit bidirectional border surfaces before interpreting absolute `nph`.
5. Compare against experimental light-yield ratios before changing nominal TiO2 or ESR reflectivity values.

## No immediate physics fix applied

No optical-physics fix was applied in this pass. The default physical modes remain:

- Hod2019/TiO2: `dielectric_dielectric`, `groundfrontpainted`, `sigmaAlpha=0.10`, `R={0.97,0.96,0.93,0.85}`.
- Hod2018/Vikuiti: `dielectric_metal`, `polishedfrontpainted`, `sigmaAlpha=0.02`, `R={0.990,0.990,0.985,0.970}`.
