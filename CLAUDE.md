# Contexto del proyecto — hodoscope-g4

> Este archivo lo lee Claude Code automáticamente al abrir el workspace.
> Mantenerlo actualizado es la forma más eficiente de evitar repetir
> contexto en cada sesión.

## Qué es esto

Simulación Geant4 del hodoscopio NA64-mini para muografía geológica,
parte de la tesis doctoral del autor en la Universidad de La Serena.

**Pregunta central de la tesis:** ¿cuál es el límite fundamental de
precisión que imponen las tolerancias geométricas y electrónicas del
detector sobre la densidad reconstruida mediante muografía?

## Quién soy

- Ingeniero Civil Electrónico (UTFSM), Magíster en Ciencias Físicas (ULS).
- Doctorado en Ciencias Físicas (ULS) en curso.
- Stack: C avanzado, C++ intermedio, Python básico-intermedio, R básico.
  ROOT (CERN) es el entorno principal de análisis.

## Cómo trabajamos

- **La física va primero, el código va segundo.** Antes de implementar,
  explicar el _por qué_ físico y verificar coherencia dimensional.
- **Unidades siempre explícitas:** `5.0 * mm`, `4.0 * GeV`. Nunca números
  desnudos.
- **Notación canónica de la tesis:** `D` (separación entre planos),
  `d` (tamaño barra), `nbars`, `T(r)` (aceptancia), `Ω` (ángulo sólido),
  `θ_D` (ángulo cenital), `F` (matriz de sistema), `γ` (opacidad),
  `ρ̂` (densidad reconstruida), `λ` (regularización).
- **Distinguir explícitamente:** resultados ya obtenidos vs hipótesis vs
  trabajo pendiente vs validaciones aún necesarias.
- **Antes de implementaciones grandes:** sugerir un MRE (minimal
  reproducible example).

## Estado actual del detector simulado (iteración 0)

### Lo que está implementado y validado

- Geometría de 32 barras EJ-200 (4 subplanos × 8 barras).
- Pintura de TiO₂ modelada como `G4OpticalSurface` (skin surface,
  finish `groundfrontpainted`, R~0.97 @ 425 nm).
- SiPMs como volúmenes lógicos sensibles (frontera lógica para conteo
  futuro de fotones).
- `PhysicsList`: FTFP_BERT + EM opt4 + Optical (registrado, semi-inerte).
- `G4UserLimits(MaxStep=0.1mm)` en EJ-200 para muestreo correcto del dE/dx.
- Generador `G4ParticleGun` controlable desde macros.
- TTree ROOT con edep, nph, tfirst por barra + info del primario.

### Validaciones cuantitativas confirmadas

- MPV de Landau ~178 keV/barra para muones MIP a 4 GeV en 1 mm de EJ-200.
- Bin central correcto en (i_X=11, j_Y=11) para haz vertical centrado.
- Asimetría X→Y en δ-rays consistente con dirección descendente del haz.

### Lo que está deliberadamente postergado

- Transporte óptico de fotones (`G4OpticalPhysics` registrada pero
  yields desactivados).
- Acoplamiento óptico SiPM-barra (requiere refactorizar: SiPM como hijo
  de la barra + `G4LogicalBorderSurface` polished).
- Pintura TiO₂ como volumen físico (sólo afecta MS, ≲0.3 mrad para
  muones MIP, sub-dominante).
- CRY (flujo cósmico realista).

## Roadmap

- [x] Iteración 0: geometría base, scoring por barra, sanity check.
- [ ] **Iteración 0.5: caracterización posicional** ← AQUÍ
  - Escaneo X (build_x_scan.py + x_resolution.C) para ver diente de sierra.
  - Predicción analítica: RMS = 1/√12 ≈ 0.289 mm en topología overlap.
- [ ] Iteración 1: activar `G4OpticalPhysics` y refactorizar SiPM coupling.
- [ ] Iteración 2: integrar CRY para flujo cósmico realista.
- [ ] Iteración 3: matriz F (sistema → píxel) y barrido de D.
- [ ] Iteración 4: análisis de propagación de errores ∂F/∂D, ∂F/∂offset.

## Gotchas conocidos del proyecto

Bugs no-obvios encontrados durante el desarrollo. Están corregidos en el código
pero documentados aquí para no volver a caer en ellos.

### G1 — `ConstructSDandField` no puede crear SDs nuevos en cada reinicialización

**Síntoma:** `G4SDManager::AddNewDetector` imprime *"Detector ScintSD already
exists"* y retorna sin registrar el nuevo SD. El primer `/run/beamOn` después de
cada `setD` produce 0 eventos porque el nuevo objeto SD no queda conectado al
framework de hits.

**Causa:** `ConstructSDandField()` es invocado por Geant4 tanto en
`/run/initialize` como en cada `ReinitializeGeometry()`. Si se hace `new
ScintillatorSD(...)` en cada llamada, el segundo y posteriores SDs son
rechazados por el `G4SDManager`.

**Fix:** comprobar si el SD ya existe antes de crearlo:
```cpp
auto* scintSD = dynamic_cast<ScintillatorSD*>(
    sdMan->FindSensitiveDetector("ScintSD", false));
if (!scintSD) {
    scintSD = new ScintillatorSD("ScintSD", "ScintHC");
    sdMan->AddNewDetector(scintSD);
}
if (fScintLV) fScintLV->SetSensitiveDetector(scintSD);
```

### G2 — `G4AnalysisManager` parsea la extensión del filename desde el **último punto**

**Síntoma:** `OpenFile()` falla silenciosamente con *"The file type 0 is not
supported"* y no crea ningún archivo ROOT en disco.

**Causa:** el `G4VFileManager` detecta el tipo de archivo extrayendo la
subcadena después del último punto del nombre. Para `d_scan_D3.0` la extensión
detectada es `.0`, que no es un tipo reconocido. Para `d_scan_D3.5` la
extensión es `.5`. Aunque `SetDefaultFileType("root")` esté activo, la
detección explícita de extensión tiene prioridad y devuelve "tipo no soportado".

**Fix:** siempre incluir `.root` explícito en `/analysis/setFileName`:
```
/analysis/setFileName d_scan_D3.0.root   # correcto
/analysis/setFileName d_scan_D3.0        # roto: extensión ".0" detectada
```

### G3 — `G4AnalysisManager::GetFileName()` devuelve valores distintos antes y después de `OpenFile()`

**Síntoma:** si se guarda `an->GetFileName()` *antes* de `OpenFile()` y se
compara con `an->GetFileName()` *después*, la comparación puede fallar aunque el
usuario no haya cambiado el nombre, desencadenando un ciclado de archivo espurio
(p. ej. cierre + apertura de `"nombre.root.root"`).

**Causa:** `OpenFile()` puede normalizar internamente el nombre (p. ej. añadir
`.root` a un nombre sin extensión), de modo que `GetFileName()` devuelve la
versión normalizada sólo a partir de ese punto.

**Fix:** guardar `fCurrentFileName` únicamente *después* de `OpenFile()`:
```cpp
an->OpenFile();
fCurrentFileName = an->GetFileName();   // captura nombre POST-apertura
```

---

## Convenciones de la base de código

- Headers en `include/`, fuentes en `src/`. Una clase por archivo.
- Naming: `CamelCase` clases, `lowerCamel` funciones, `f`+`PascalCase`
  miembros (Geant4 standard).
- Comentarios en español (idioma de trabajo).
- Mensajes `G4cout` en inglés (compatibilidad logs).
- Build: CMake fuera de source (`build/`), Geant4 ≥ 11, C++17.

## Comandos frecuentes

```bash
# Build
cd build && cmake .. && make -j$(nproc)

# Sanity check
./hodoscope ../macros/run_mip_central.mac
root -l '../analysis/quick_look.C("hodoscope.root")'

# Escaneo posicional
cd ../analysis && python build_x_scan.py
cd ../build && ./hodoscope ../analysis/x_scan.mac
root -l '../analysis/x_resolution.C("hodoscope.root")'

# Reset rápido
rm -f *.root *.png
```

## Repositorio remoto

`https://github.com/dowiyogo/hodoscope`
