#!/usr/bin/env python3
"""
build_x_scan.py
---------------

Genera un macro Geant4 para escanear posicionalmente el eje X (con y=0
fijo) y mapear la respuesta del hodoscopio en función de la posición de
incidencia. Es el insumo experimental para verificar la resolución
sub-barra dada por el offset entre X-sup y X-inf.

Diseño:
- Grilla por defecto: x ∈ [-6, +6] mm con dx = 0.2 mm  → 61 puntos.
- 200 muones MIP a 4 GeV por punto verticales (n*z=-1).
- Total: 61 * 200 = 12 200 eventos. Tiempo serial ~30-60 s.
- Salida: archivo .mac listo para `./hodoscope x_scan.mac`.

Estructura física esperada:
- Cada 1 mm de x_true corresponde a un patrón único de barras
  encendidas (intersección X-sup ∩ X-inf).
- x_reco - x_true debe ser uniforme en [-0.5, +0.5] mm con RMS ~0.29 mm.

Uso típico:
    python build_x_scan.py
    cd ../build && ./hodoscope ../x_scan.mac
    root -l '../analysis/x_resolution.C("hodoscope.root")'
"""
import argparse
import numpy as np
from pathlib import Path


def build(args):
    xs = np.arange(args.xmin, args.xmax + 1e-9, args.dx)

    header = [
        "# x_scan.mac  -  generado por analysis/build_x_scan.py",
        f"# Grilla: {len(xs)} puntos en X ∈ [{args.xmin}, {args.xmax}] mm, dx = {args.dx} mm",
        f"# Y fijo = {args.y} mm   (haz vertical)",
        f"# N muones por punto: {args.n}",
        f"# Total eventos: {len(xs)*args.n}",
        f"# Energía: {args.energy} GeV",
        "",
        "/run/initialize",
        "",
        "# Output a x_scan.root (NO sobrescribe hodoscope.root del sanity check)",
        "/analysis/setFileName x_scan",
        "",
        "/hodoscope/det/setD 5.0 mm",
        "/hodoscope/det/optical false",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "",
        "/run/printProgress 2000",
        "",
    ]

    body = []
    for x in xs:
        body.append(f"/gun/position {x:.4f} {args.y:.4f} 50.0 mm")
        body.append(f"/run/beamOn {args.n}")

    out = Path(args.out)
    out.write_text("\n".join(header + body) + "\n")
    print(f"[OK] {len(xs)} puntos × {args.n} muones = "
          f"{len(xs)*args.n} eventos -> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--xmin",   type=float, default=-6.0, help="X mínimo [mm]")
    p.add_argument("--xmax",   type=float, default=+6.0, help="X máximo [mm]")
    p.add_argument("--dx",     type=float, default= 0.2, help="paso en X [mm]")
    p.add_argument("--y",      type=float, default= 0.0, help="Y fijo [mm]")
    p.add_argument("--n",      type=int,   default= 200, help="muones por punto")
    p.add_argument("--energy", type=float, default= 4.0, help="energía cinética [GeV]")
    p.add_argument("--out",    type=str,   default="x_scan.mac")
    build(p.parse_args())
