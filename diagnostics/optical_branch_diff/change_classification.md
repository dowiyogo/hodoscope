# Change classification

| Archivo | Cambio observado | Categoría | ¿Portar? | Motivo |
| --- | --- | --- | --- | --- |
| `src/PhysicsList.cc` | La rama funcional registraba `G4OpticalPhysics` sólo con `HODO_ENABLE_OPTICAL=1` y agregaba logs. La rama MT ya registra física óptica y produce tracks ópticos. | A / E | No | No es la causa raíz y cambiarlo podría alterar el comportamiento MT actual. |
| `src/DetectorConstruction.cc` | Agrega `RINDEX=3.5` al material `G4_Si`. | B | Sí | Necesario para una interfaz óptica válida hacia el SiPM. |
| `src/DetectorConstruction.cc` | Guarda `Scint_PV` y `SiPM_PV` por barra. | B | Sí | Necesario para crear `G4LogicalBorderSurface` por par físico. |
| `src/DetectorConstruction.cc` | Elimina el gap de `50 um` sólo cuando improved optical está enabled. | B | Sí | Es el cambio mínimo de acople geométrico sin romper Iteración 0 por defecto. |
| `src/DetectorConstruction.cc` | Reemplaza la skin global por border surfaces en modo improved. | B | Sí, integrado | Se porta preservando la rama TiO2/Vikuiti ya existente en MT. |
| `src/DetectorConstruction.cc` | En la rama funcional el reflector improved usa `polishedfrontpainted` para subir eficiencia. | E | No literal | En MT debe preservarse la diferenciación física: TiO2 diffuse `groundfrontpainted`, Vikuiti specular `polishedfrontpainted`. |
| `include/DetectorConstruction.hh` | Agrega flag `fUseImprovedOpticalCoupling`, getter, setter y vectores de PVs. | B | Sí | Estado mínimo para activar el acople mejorado detrás de flag default `false`. |
| `include/DetectorMessenger.hh` | Agrega comando `/hodoscope/det/improvedOptical`. | B | Sí | Necesario para activar el fix desde macros sin cambiar defaults. |
| `src/DetectorMessenger.cc` | Implementa el comando `/hodoscope/det/improvedOptical`. | B | Sí | Necesario para control runtime. |
| `src/RunAction.cc` | Registra `improved_optical_coupling` en sidecar y logs. | D | Sí | No cambia TTree; ayuda a verificar qué geometría óptica produjo el ROOT. |
| `src/SiPMSD.cc` | Sin cambios entre ramas. | C | No | El SD ya cuenta fotones al entrar en `SiPM_LV`. |
| `include/SiPMSD.hh` | Sin cambios entre ramas. | C | No | No se requiere cambio de interfaz ni scoring. |
| `src/ScintillatorSD.cc` | Sin cambios relevantes para el fix. | E | No | Restricción explícita: no tocar scoring de `edep`. |
| `src/RunAction.cc` | Lógica MT de escritura/merge ya existe en `feat/multithreading`. | E | No extra | Se preserva; no se copia lógica incompatible o redundante. |
| `hodoscope.cc` | La rama funcional agrega logs de `HODO_ENABLE_OPTICAL`; MT mantiene `G4RunManagerType::Default`. | D / E | No | No es necesario para recuperar `nph`; no se toca el run manager. |
| `CMakeLists.txt` | Agrega `BUILD_OPTICAL_UNIT_TEST` y `test_optical`. | D | No | Diagnóstico aislado, no fix mínimo para el detector MT. |
| `test_optical/` | Test unitario óptico aislado. | D | No | Útil históricamente, pero no necesario para este port mínimo. |
| `analysis/iteration1_optical_validation/*` | Scripts/macros/documentos de validación de la rama óptica. | D / E | No | Evitar mezclar análisis no necesario. |
| `macros/optical_tests/run_variant_*_quick.mac` | Macros de MT para comparar variantes. | D | Sí | Se actualizan sólo para activar `/hodoscope/det/improvedOptical true`. |
