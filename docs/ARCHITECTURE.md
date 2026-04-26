# Arquitectura — hodoscope-g4

Decisiones de diseño y notación, vinculadas a la pregunta central de la
tesis: *¿cuál es el límite de precisión que imponen las tolerancias
geométricas y electrónicas sobre la densidad reconstruida?*

## 1. Sistema de coordenadas

```
                +Z (cosmics caen en -Z)
                 |
   ┌─── X-sup ───┐  z = +(D + 2·t_bar + sepZ)/2
   ┌─── X-inf ───┐  z = +(D + sepZ)/2
        ↕  D = 5 mm
   ┌─── Y-sup ───┐  z = -(D + sepZ)/2
   ┌─── Y-inf ───┐  z = -(D + 2·t_bar + sepZ)/2
                 |
                 +X →
```

- El asamble está centrado en (0, 0, 0) del *World*.
- **Plano X** mide la coordenada **X** del muón → barras orientadas largas en Y, separadas en X.
- **Plano Y** mide la coordenada **Y** → barras largas en X, separadas en Y.

## 2. Notación (consistente con la tesis)

| Símbolo | Significado | Default |
|--------:|-------------|--------:|
| `D`     | separación entre planos X e Y | 5 mm |
| `d`     | tamaño lateral de la barra (= ancho) | 3 mm |
| `nbars` | número de barras por subplano | 8 |
| `gap`   | aire entre barras paralelas | 1 mm |
| `sepZ`  | separación vertical entre subplanos sup-inf | 2 mm |
| `offset`| desplazamiento del subplano inferior | 2 mm |
| `t_bar` | espesor de barra | 1 mm |
| `L_bar` | largo de barra | 75 mm |
| `t_paint` | espesor de pintura TiO₂ (no instanciado, sólo en surface) | 50 μm |

## 3. Materiales

| Material | Densidad | Uso | Propiedades ópticas |
|----------|---------:|-----|---------------------|
| Air (NIST G4_AIR) | 1.2e-3 g/cm³ | World, asamble | RINDEX = 1.0003 |
| EJ-200 | 1.023 g/cm³ | barras de centellador | RINDEX 1.58, λ_atenuación 3.8 m, yield 10000/MeV, τ 2.1 ns |
| Si (NIST G4_Si) | 2.33 g/cm³ | placeholder SiPM | (sin propiedades ópticas) |
| TiO₂ (rutilo) | 4.06 g/cm³ | pintura externa | sólo via `G4OpticalSurface` |

## 4. Modelado de la pintura TiO₂

**Decisión:** modelar la pintura como `G4OpticalSurface` con finish
`groundfrontpainted` aplicado como `G4LogicalSkinSurface` sobre el LV de
las barras. **No** se instancia un volumen físico de TiO₂.

**Justificación.**

| Aspecto | Surface (elegido) | Volumen físico |
|---------|-------------------|----------------|
| Efecto óptico | Reflexión Lambertiana realista | Requiere modelar transporte dentro del TiO₂ (innecesario) |
| Multiple scattering del muón | Despreciado | Capturado |
| Costo computacional | Mínimo | Mayor |
| Realismo a 50 μm | ★★★★★ | ★★★★ |

Para 50 μm de TiO₂ a 4 GeV, el MS adicional es ~0.3 mrad por traversal,
sub-dominante respecto a los ~11 mrad intrínsecos por la separación
D=5 mm. Si en una iteración futura se quiere cuantificar este aporte, el
material `TiO2_paint` ya está definido y se puede envolver la barra en un
*shell* fino.

**Reflectividad usada (típica EJ-510):**

| Energía | λ | Reflectividad |
|--------:|--:|--------------:|
| 2.38 eV | 520 nm | 0.97 |
| 2.70 eV | 460 nm | 0.96 |
| 2.92 eV | 425 nm | 0.93 |
| 3.10 eV | 400 nm | 0.85 |

**Limitación documentada:** la skin pinta las 6 caras incluyendo la del
acoplamiento al SiPM. Mientras `G4OpticalPhysics` esté off, esto es
inerte. Cuando se active, hay que añadir
`G4LogicalBorderSurface(bar_PV, sipm_PV)` con finish `polished`.

## 5. Física activa

`G4VModularPhysicsList` con:

- `G4DecayPhysics`
- `G4RadioactiveDecayPhysics`
- `G4EmStandardPhysics_option4`
- `G4HadronElasticPhysics`
- `G4HadronPhysicsFTFP_BERT`
- `G4StoppingPhysics`
- `G4IonPhysics`
- `G4OpticalPhysics` (registrado, semi-inerte hasta activar yields/transport)

**Cuts:** 0.1 mm para gamma, e±. **MaxStep en EJ-200:** 0.1 mm (vía
`G4UserLimits`) para muestrear correctamente el dE/dx en barras de 1 mm.

## 6. Scoring

Dos `G4VSensitiveDetector`:

- `ScintillatorSD` aplicado a `Scint_LV` → 32 hits (uno por copyNo). Cada
  hit acumula `edep`, `tFirst`, `posEntry`, `posExit`.
- `SiPMSD` aplicado a `SiPM_LV` → 32 hits. Cuenta opticalphotons que
  entran al volumen y los aniquila (modelo "absorbedor perfecto").
  Inerte hasta que el transporte óptico esté activo.

`EventAction` colapsa los 32 hits de cada SD en columnas escalares del
TTree (`edep_00..edep_31`, `nph_00..nph_31`, `tfirst_00..tfirst_31`).

## 7. Generador

`G4ParticleGun` controlable desde macro vía comandos estándar
`/gun/particle`, `/gun/energy`, `/gun/position`, `/gun/direction`. Para
muones cósmicos reales se conectará CRY (interfaz oficial Geant4) en una
iteración futura.

## 8. Mapa de la respuesta del detector

El píxel reconstruido es el par (`i_X`, `j_Y`) ∈ [0,15]² de las barras
con mayor `edep` en cada plano X e Y. Para eventos en zona de overlap
(1 mm dentro de cada subplano de 4 mm de pitch), el cociente de edep
entre dos barras adyacentes permite triangular sub-mm.

Estos detalles son el insumo para construir más adelante la matriz de
sistema **F** (sección 8 del documento de geometría original).

## 9. Convenciones de código

- Headers en `include/`, fuentes en `src/`. Nada de templates pesados.
- Una clase por archivo. Nombres en `CamelCase` para clases, `lowerCamel`
  para funciones, `f`+`PascalCase` para miembros (Geant4 standard).
- Unidades **siempre explícitas**: `5.0 * mm`, `4.0 * GeV`. Nunca números
  desnudos en geometría/física.
- Comentarios en español (idioma de trabajo). Mensajes `G4cout` en inglés
  para compatibilidad con logs estándar Geant4.
