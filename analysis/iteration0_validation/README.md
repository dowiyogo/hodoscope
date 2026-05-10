# Iteration 0 Validation Suite

Esta carpeta contiene la suite mínima, reproducible y ordenada para cerrar
la Iteración 0 del hodoscopio NA64-mini antes de pasar a Iteración 1.

## Qué valida

- Geometría activa del detector.
- Salida ROOT válida.
- Scoring de energía depositada por barra.
- Tiempo del primer hit por barra.
- Consistencia single-thread vs multithread.
- Integridad de los scripts de análisis existentes.
- Producción de figuras y tablas resumen en una sola carpeta.

Esta suite no activa transporte óptico, no reescribe la geometría y no cambia
la estructura principal del proyecto.

## Estructura

- `macros/`: macros batch pequeñas y reproducibles.
- `scripts/`: utilidades Python para inspección y resumen del ROOT.
- `outputs/`: archivos generados por la validación. Esta carpeta se ignora en git.
- `run_iteration0_validation.sh`: script maestro de ejecución.
- `ITERATION0_VALIDATION_SUMMARY.md`: resumen final generado por la corrida.

## Requisitos

- Build previo del proyecto en `build/`.
- `bash`, `python3` y el módulo Python de ROOT.
- `geant4-config` disponible si se desea reportar la versión de Geant4.

## Cómo correrla

Desde la raíz del repositorio:

```bash
bash analysis/iteration0_validation/run_iteration0_validation.sh
```

El script maestro:

- recompila el proyecto si es necesario,
- crea `outputs/root`, `outputs/tables`, `outputs/figures` y `outputs/logs`,
- corre las seis macros batch (ST y MT para centro, X e Y),
- ejecuta los análisis,
- genera `ITERATION0_VALIDATION_SUMMARY.md`.

## Archivos generados

La corrida produce, como mínimo:

- `outputs/root/*.root`
- `outputs/tables/*.csv`
- `outputs/tables/*.md`
- `outputs/tables/*.json`
- `outputs/figures/*.png`
- `outputs/logs/*.log`

## Criterios de aceptación

A. El proyecto compila sin errores.
B. Las macros batch corren sin visualización.
C. Se generan archivos ROOT válidos.
D. El TTree esperado existe.
E. Las ramas esperadas existen.
F. Para un muón central, las barras esperadas tienen `edep > 0`.
G. El número de barras activadas por evento es compatible con la geometría.
H. La energía total depositada es positiva y razonable para MIPs.
I. ST y MT entregan distribuciones compatibles dentro de tolerancias estadísticas.
J. No se introduce física óptica.

## Flujo recomendado

1. Construir el ejecutable.
2. Ejecutar esta suite.
3. Revisar `ITERATION0_VALIDATION_SUMMARY.md` y los archivos en `outputs/`.
4. Si aparece una discrepancia geométrica o de scoring, corregirla antes de iniciar Iteración 1.
