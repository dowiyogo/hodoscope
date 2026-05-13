# Root cause from working branch

## 1. ¿Cuál fue la causa raíz de nph = 0?

La causa raíz fue transporte/acople óptico entre la barra y el SiPM, no la producción de fotones. La rama funcional diagnosticó que la `G4LogicalSkinSurface` sobre `Scint_LV` pintaba todas las caras, incluida la cara de lectura, y que además el SiPM tenía un gap de aire de `50 um` sin una `G4LogicalBorderSurface` que permitiera un acople óptico controlado hacia `SiPM_LV`.

El TTree cuenta `nph` por el camino existente de `SiPMSD::ProcessHits`, es decir, cuando el fotón entra al volumen `SiPM_LV`. Por eso el fix robusto no es depender de `Detection` en una frontera `dielectric_metal`, sino permitir que los fotones entren al volumen SiPM.

## 2. ¿Qué archivo(s) se modificaron para corregirlo?

El fix real de la rama funcional tocó:

- `include/DetectorConstruction.hh`
- `include/DetectorMessenger.hh`
- `src/DetectorConstruction.cc`
- `src/DetectorMessenger.cc`
- `src/RunAction.cc`

También hubo cambios de diagnóstico/test en `CMakeLists.txt`, `test_optical/`, macros y documentos.

## 3. ¿El fix estuvo en PhysicsList?

No como causa raíz. `G4OpticalPhysics` y `G4Scintillation` ya podían producir fotones. La rama funcional agregó logs/env para `HODO_ENABLE_OPTICAL`, pero el diagnóstico explícitamente descartó PhysicsList como causa primaria.

## 4. ¿El fix estuvo en DetectorConstruction?

Sí. El fix real está principalmente en `DetectorConstruction`: RINDEX para Si, gap SiPM removido bajo flag, tracking de pares `Scint_PV`/`SiPM_PV`, y superficies `G4LogicalBorderSurface` para reflector y acople SiPM.

## 5. ¿El fix estuvo en SiPMSD?

No. `src/SiPMSD.cc` no se modificó. Se preservó el conteo existente por volumen: cada `G4OpticalPhoton` que entra en `SiPM_LV` incrementa `nPhotons` y se mata.

## 6. ¿El fix estuvo en geometría/acople barra-SiPM?

Sí. Esta fue la parte central: contacto directo barra-SiPM bajo `/hodoscope/det/improvedOptical true`, eliminación del gap de `50 um`, border surface `Scint_PV -> SiPM_PV`, y evitar que el reflector pinte la cara de lectura.

## 7. ¿El fix estuvo en propiedades ópticas de materiales?

Parcialmente. EJ-200 y aire ya tenían MPT ópticas. La parte material necesaria que faltaba para el acople robusto fue agregar `RINDEX=3.5` al material `G4_Si` usado por el SiPM.

## 8. ¿El fix estuvo en CMake/test unitario?

No para el detector real. `CMakeLists.txt` y `test_optical/` fueron infraestructura diagnóstica para probar el mecanismo aislado. No son necesarios para recuperar `nph > 0` en `feat/multithreading`.

## 9. ¿Qué parte es diagnóstico/test y qué parte es fix real?

Diagnóstico/test:

- `test_optical/`
- `BUILD_OPTICAL_UNIT_TEST`
- macros de validación aislada
- documentos y logs de `diagnostics/optical_photon_root_cause/`

Fix real:

- flag `/hodoscope/det/improvedOptical`
- almacenamiento de `Scint_PV` y `SiPM_PV`
- contacto directo SiPM-barra bajo flag
- border surfaces `Scint -> assembly air` y `Scint -> SiPM`
- `RINDEX` del Si
- logging/sidecar del flag improved

## 10. ¿Qué cambios son seguros de portar a feat/multithreading?

Son seguros de portar:

- el flag `/hodoscope/det/improvedOptical`, default `false`;
- `RINDEX=3.5` para `G4_Si`;
- almacenamiento de pares de physical volumes;
- gap SiPM removido sólo con el flag enabled;
- border surfaces en el modo improved;
- logging del flag en `RunAction`.

No se portan el test unitario, cambios de análisis no necesarios, ni cambios que reemplacen el modelo TiO2/Vikuiti ya implementado en `feat/multithreading`.
