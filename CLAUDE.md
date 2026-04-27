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
- σ_overlap = 0.337 mm (plano en D ∈ [3,8] mm); exceso +17% sobre 1/√12
  atribuido a δ-rays y fluctuaciones Landau (no a discretización del scan).
- f_overlap ≈ 0.495, f_delta ≈ 0.0034, constantes en D.
- **Iter 0.7 (scan 2D 31×31 mm², 961×200 muones):**
  - `<edep_total>` zona central = 0.558 MeV, rms/mean = 23.2% (uniforme).
  - Eficiencia geométrica central = 1.000 (cae a 0 en gaps ±14 mm).
  - Cramér's V (correlación topológica X–Y) = 0.028 < 0.05 → planos ortogonales.
  - Píxeles virtuales overlap×overlap: 225/256 activados (31 en bordes sin overlap).

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
- [x] Iteración 0.5: caracterización posicional (σ_overlap=0.337 mm, barrido D).
- [x] Iteración 0.7: caracterización 2D single-hodoscopio ← rama `feat/single-hodoscope-characterization`
  - Scan 2D 31×31 mm², uniformidad, eficiencia, Cramér's V=0.028, 225/256 píxeles.
- [x] Iteración aux: multithreading (×6.7 speedup) ← rama `feat/multithreading`
- [ ] Iteración 1.0: telescopio de dos módulos para σ_θ real ← rama `feat/telescope-two-modules` (futura, desde `main`).
- [ ] Iteración 1.x: activar `G4OpticalPhysics` y refactorizar SiPM coupling.
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

### G4 — `SetNtupleMerging(true)` es incompatible con el ciclado manual de archivos en MT

**Síntoma:** en modo MT, llamar a `CloseFile(false)` + `OpenFile()` dentro de
`BeginOfRunAction` para cambiar de archivo entre valores de D produce
corrupción o pérdida de eventos: los hilos worker siguen escribiendo al archivo
antiguo mientras el maestro ya abrió uno nuevo.

**Causa:** `SetNtupleMerging(true)` hace que Geant4 cree un NTuple por hilo
y los fusione al cerrar. El ciclo manual rompe esa sincronización porque los
workers no reciben la señal de cierre entre `BeamOn` consecutivos.

**Fix:** en modo MT desactivar el ciclado con `fAllowFileCycling = false` (el
default). El barrido en D que requiere múltiples archivos debe hacerse en
modo serial (`G4RunManagerType::Serial`) con `fAllowFileCycling = true`, o
bien lanzando el ejecutable una vez por valor de D.

```cpp
// RunAction.cc — en BeginOfRunAction:
if (!G4Threading::IsMasterThread()) return;
// ...
} else if (fAllowFileCycling && reqName != fCurrentFileName) {
    // sólo alcanzable en modo serial con fAllowFileCycling=true
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

## Estructura de ramas

| Rama | Propósito | Estado |
|------|-----------|--------|
| `main` | Iteraciones validadas y cerradas | estable |
| `feat/single-hodoscope-characterization` | Iter 0.7: caracterización 2D del hodoscopio único (uniformidad, eficiencia, bordes) | activa |
| `feat/telescope-two-modules` | Iter 1.x: geometría de dos módulos para σ_θ real (refactor DetectorConstruction) | **futura** — crear desde `main`, no desde la rama activa |

**Decisión de diseño:** la medición de resolución angular real (σ_θ ≈ d_eff/D) requiere un segundo módulo hodoscopio como referencia downstream. Esa refactorización va en su propia rama para aislarla del trabajo de caracterización del hodoscopio único. No mezclar.

## Repositorio remoto

`https://github.com/dowiyogo/hodoscope`
