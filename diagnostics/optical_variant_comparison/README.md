# Optical variant comparison

- Branch: `feat/multithreading`
- Initial commit: `f27528813032ff6ec22b33bdd76cf0da3f2d3bb7`

## Objective

Differentiate the optical reflector model for the two supported detector variants:

- Hod2019 / TiO2 paint: diffuse Lambertian-like reflection.
- Hod2018 / Vikuiti ESR: mostly specular high-reflectivity reflection.

## Previous optical state

The preceding optical root-cause work reported nonzero SiPM photon counts:

- Unit test: `detected_over_generated = 0.0812458`
- Real detector: `mean nph/evento = 285.97`
- Real detector: `100/100` events with `nph > 0`

That makes the optical signal observable enough to compare reflector variants.

## Physical expectation

TiO2 paint is modeled as a diffuse `groundfrontpainted` dielectric-dielectric optical surface with reflectivity near `0.93-0.97` around the EJ-200 emission peak.

Vikuiti ESR is modeled as a specular `polishedfrontpainted` dielectric-metal optical surface with reflectivity near `0.985-0.995` around the EJ-200 emission peak.

Because Vikuiti is both more reflective and more specular, it is expected to collect more photons at the MPPC than TiO2 in otherwise equivalent runs.

## Known limitation

The reflector is still represented as a `G4LogicalSkinSurface` on the full `fScintLV`. That means the same skin can also apply to the face pointing toward the SiPM. This limitation is documented here but not refactored in this task; a later iteration should replace the SiPM-facing face with a dedicated `G4LogicalBorderSurface`.
