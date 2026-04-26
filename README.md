# hodoscope-g4

Simulación Geant4 mínima del hodoscopio NA64-mini para muografía geológica
(Universidad de La Serena).

> Estado: **iteración 0 — geometría + scoring por barra, sin transporte óptico activo**.
> El detector se modela con barras de EJ-200, pintura externa de TiO₂
> (modelada como `G4OpticalSurface`), y SiPMs como volúmenes lógicos
> sensibles que más adelante contarán fotones.

## Contenido

```
hodoscope-g4/
├── CMakeLists.txt
├── hodoscope.cc                  # main del programa
├── include/                      # headers
│   ├── DetectorConstruction.hh   # geometría + materiales + superficies
│   ├── DetectorMessenger.hh      # comandos UI /hodoscope/det/*
│   ├── PhysicsList.hh            # FTFP_BERT + EM opt4 + Optical (preparado)
│   ├── PrimaryGeneratorAction.hh # G4ParticleGun (controlable desde macro)
│   ├── ActionInitialization.hh
│   ├── RunAction.hh              # crea TTree ROOT
│   ├── EventAction.hh            # llena TTree por evento
│   ├── HodoscopeHit.hh           # hit unificado bar/SiPM
│   ├── ScintillatorSD.hh         # SD para las 32 barras
│   └── SiPMSD.hh                 # SD para los 32 SiPMs (cuenta optical photons)
├── src/                          # implementación de los headers
├── macros/
│   ├── init_vis.mac              # inicialización modo interactivo
│   ├── vis.mac                   # visualización OGL/Qt
│   ├── run_mip_central.mac       # 1k muones MIP centrados
│   ├── scan_xy.mac               # escaneo grueso (foreach)
│   ├── scan_one_y.mac            # auxiliares del foreach
│   └── scan_one_xy.mac
├── analysis/
│   ├── quick_look.C              # inspección rápida con ROOT/CINT
│   └── build_scan_macro.py       # generador de macro de escaneo fino
└── docs/
    └── ARCHITECTURE.md           # decisiones de diseño y notación
```

## Compilación

Requisitos:
- Geant4 ≥ 11.0 con ROOT, Qt y OpenGL (`-DGEANT4_USE_QT=ON -DGEANT4_USE_OPENGL_X11=ON -DGEANT4_USE_GDML=ON`).
- CMake ≥ 3.16.
- Compilador C++17.

```bash
git clone https://github.com/dowiyogo/hodoscope.git
cd hodoscope
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## Ejecución

### Modo interactivo (visualización)

```bash
./hodoscope
```

Se abre una sesión Qt con el detector dibujado. Para disparar un muón:

```
Idle> /run/beamOn 1
```

### Modo batch (producción)

```bash
./hodoscope run_mip_central.mac
root -l 'analysis/quick_look.C("hodoscope.root")'
```

## Comandos del messenger

```
/hodoscope/det/setD <valor> <unidad>     # separación entre planos X y Y (default 5 mm)
/hodoscope/det/optical <true|false>      # flag para futuro encendido óptico
```

Para barrer la separación crítica D y estudiar su efecto en la resolución
angular:

```
/hodoscope/det/setD 4.5 mm
/run/beamOn 10000
/hodoscope/det/setD 5.0 mm
/run/beamOn 10000
/hodoscope/det/setD 5.5 mm
/run/beamOn 10000
```

## Salida

`hodoscope.root` contiene un `TTree` llamado `hodo` con:

| Branch        | Tipo          | Significado                                  |
|---------------|---------------|----------------------------------------------|
| `eventID`     | `int`         | Índice del evento                            |
| `prim_x/y/z`  | `double` [mm] | Posición de generación del muón              |
| `prim_px/py/pz` | `double`    | Dirección unitaria del muón                  |
| `prim_E`      | `double` [MeV]| Energía cinética inicial                     |
| `edep_NN`     | `double` [MeV]| Energía depositada en barra `NN` (00..31)    |
| `nph_NN`      | `int`         | Fotones detectados en SiPM `NN` (futuro)     |
| `tfirst_NN`   | `double` [ns] | Tiempo del primer hit en barra `NN`          |

Indexación de barras:

| `NN` rango | Subplano  | Lado SiPM   |
|-----------:|-----------|-------------|
| 00 – 07    | X-sup     | Y negativo  |
| 08 – 15    | X-inf     | Y positivo  |
| 16 – 23    | Y-sup     | X negativo  |
| 24 – 31    | Y-inf     | X positivo  |

## Limitaciones conocidas (iteración 0)

1. **Transporte óptico desactivado.** Las propiedades ópticas (RINDEX,
   ABSLENGTH, SCINTILLATIONYIELD) y la `G4OpticalSurface` de TiO₂ están
   definidas pero inertes. Se activan registrando `G4OpticalPhysics` en
   modo activo.
2. **Acoplamiento SiPM-barra simplificado.** En la geometría actual el
   SiPM está separado por ~50 μm de aire. Cuando se active el transporte
   óptico, hay que reestructurar: SiPM como hijo del volumen de barra +
   `G4LogicalBorderSurface(bar_PV, sipm_PV)` con finish `polished`.
3. **Pintura TiO₂ sin volumen físico.** El material `TiO2_paint` está
   definido pero no instanciado como volumen. Su efecto óptico está en
   la `G4LogicalSkinSurface`. El aporte al multiple scattering (≲0.3 mrad
   por capa para muones de 4 GeV) está despreciado en esta iteración.
4. **Generador simple.** `G4ParticleGun` con dirección fija. Para muones
   cósmicos reales hay que conectar CRY (PARMA o similar) en una
   iteración posterior.

## Roadmap

- [ ] Iteración 1: activar `G4OpticalPhysics` y refactorizar acoplamiento SiPM.
- [ ] Iteración 2: integrar CRY para flujo cósmico realista.
- [ ] Iteración 3: implementar el cálculo de la matriz F (sistema → píxel).
- [ ] Iteración 4: análisis de propagación de errores ∂F/∂D, ∂F/∂offset.

## Estudios incluidos en `analysis/`

### 1. Sanity check (`quick_look.C`)

Histograma de píxel reconstruido y suma de edep por plano. Para un haz
vertical centrado se debe ver un único bin brillante en el centro y MPV
≈ 178 keV (1 MIP) en ambos planos.

```bash
./hodoscope run_mip_central.mac
root -l '../analysis/quick_look.C("hodoscope.root")'
```

### 2. Resolución posicional X (`build_x_scan.py` + `x_resolution.C`)

Verifica el "truco del offset" entre X-sup y X-inf. Predicción analítica:
cada 1 mm de x_true mapea a un patrón único de barras encendidas
(16 píxeles virtuales de 1 mm en lugar de 8 píxeles físicos de 3 mm).
Residual `x_reco - x_true` uniforme en [-0.5, +0.5] mm con
**RMS = 1/√12 ≈ 0.289 mm**.

```bash
cd analysis/
python build_x_scan.py                          # genera x_scan.mac
cd ../build/
./hodoscope ../x_scan.mac                       # ~30-60 s serial
root -l '../analysis/x_resolution.C("hodoscope.root")'
```

Salida: tres figuras (`edep_vs_x.png`, `p_fires_vs_x.png`,
`residual.png`) y un reporte por consola con la distribución de
topologías y el RMS del residual.

### 3. Zoom sobre la zona de overlap (`build_overlap_zoom.py`)

Escaneo ultra-fino en x ∈ [-2, +2] mm con dx = 0.05 mm. Sirve para
caracterizar la transición geométrica entre topologías y, en una
iteración futura con óptica activa, para mapear el cociente de cargas
Q_sup/(Q_sup+Q_inf) que da el sub-mm real.

```bash
cd analysis/ && python build_overlap_zoom.py
cd ../build/ && ./hodoscope ../overlap_zoom.mac
root -l '../analysis/x_resolution.C("hodoscope.root")'
```

## Autor

René Ríos — Universidad de La Serena
Doctorado en Ciencias Físicas
2026
