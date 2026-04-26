#!/usr/bin/env python3
"""
build_xy_scan.py
----------------

Genera un macro Geant4 para el scan 2D del hodoscopio único (iteración 0.7).

Diseño:
- Grilla 2D: x ∈ [xmin, xmax], y ∈ [ymin, ymax], paso dxy = 1 mm.
  Default: 31 × 31 = 961 posiciones en [−15, +15] mm.
- N muones MIP a 4 GeV verticales por punto (default: 200).
- Total eventos: 961 × 200 = 192 200.
- Output: archivo ÚNICO xy_scan.root (no por punto). El TTree guarda
  prim_x y prim_y por evento, así el análisis separa por celda en post-hoc.
  (Gotcha G2: extensión .root explícita en setFileName.)

Uso típico:
    python analysis/build_xy_scan.py
    cd build && ./hodoscope ../macros_generados/xy_scan.mac
    root -l '../analysis/xy_uniformity.C("xy_scan.root")'
"""

import argparse
import numpy as np
from pathlib import Path


def build(args):
    xs = np.arange(args.xmin, args.xmax + 1e-9, args.dxy)
    ys = np.arange(args.ymin, args.ymax + 1e-9, args.dxy)

    n_x     = len(xs)
    n_y     = len(ys)
    n_total = n_x * n_y * args.n

    header = [
        "# xy_scan.mac  -  generado por analysis/build_xy_scan.py",
        f"# Grilla 2D: x ∈ [{args.xmin}, {args.xmax}] mm, y ∈ [{args.ymin}, {args.ymax}] mm",
        f"# paso dxy = {args.dxy} mm  →  {n_x} × {n_y} = {n_x * n_y} posiciones",
        f"# N muones por punto: {args.n}",
        f"# Total eventos: {n_total}   (beamOn calls: {n_x * n_y})",
        f"# Energía: {args.energy} GeV  |  D = {args.D} mm",
        "",
        "/run/initialize",
        "",
        f"/hodoscope/det/setD {args.D:.1f} mm",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "",
        f"/analysis/setFileName {args.out_root}",
        "",
        "/run/printProgress 1000",
        "",
    ]

    body = []
    for y in ys:
        for x in xs:
            body.append(f"/gun/position {x:.4f} {y:.4f} 50.0 mm")
            body.append(f"/run/beamOn {args.n}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(header + body) + "\n")

    n_beamon = n_x * n_y
    print(f"[OK] {n_x} × {n_y} posiciones × {args.n} muones/punto = {n_total} eventos")
    print(f"     /run/beamOn calls: {n_beamon}  (debe ser {n_x} × {n_y} = {n_beamon})")
    print(f"     Macro escrito en: {out}")
    print(f"     Root file: {args.out_root}")
    print()
    print("Para correr el scan:")
    print(f"  cd build && ./hodoscope ../{out}")
    print()
    print("Para analizar (desde build/):")
    print(f'  root -l \'../analysis/xy_uniformity.C("{args.out_root}")\'')


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--xmin",     type=float, default=-15.0,
                   help="X mínimo [mm]  (default: -15.0)")
    p.add_argument("--xmax",     type=float, default=+15.0,
                   help="X máximo [mm]  (default: +15.0)")
    p.add_argument("--ymin",     type=float, default=-15.0,
                   help="Y mínimo [mm]  (default: -15.0)")
    p.add_argument("--ymax",     type=float, default=+15.0,
                   help="Y máximo [mm]  (default: +15.0)")
    p.add_argument("--dxy",      type=float, default=1.0,
                   help="Paso de la grilla [mm]  (default: 1.0)")
    p.add_argument("--n",        type=int,   default=200,
                   help="Muones por punto  (default: 200)")
    p.add_argument("--energy",   type=float, default=4.0,
                   help="Energía cinética [GeV]  (default: 4.0)")
    p.add_argument("--D",        type=float, default=5.0,
                   help="Separación entre planos D [mm]  (default: 5.0)")
    p.add_argument("--out-root", type=str,   default="xy_scan.root",
                   dest="out_root",
                   help="Nombre del archivo ROOT de salida  (default: xy_scan.root)")
    p.add_argument("--out",      type=str,
                   default="macros_generados/xy_scan.mac",
                   help="Ruta de salida del macro  (default: macros_generados/xy_scan.mac)")
    build(p.parse_args())
