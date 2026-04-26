#!/usr/bin/env python3
"""
build_scan_macro.py
-------------------

Genera un macro Geant4 que escanea (X, Y) con un grano arbitrario y N
muones por punto. Se usa cuando /control/foreach con listas largas se
vuelve incómodo.

Uso:
    python build_scan_macro.py --xmin -15 --xmax 15 --dx 0.5 \\
                               --ymin -15 --ymax 15 --dy 0.5 \\
                               --n 100 --energy 4.0 \\
                               --out scan_fine.mac

Salida: macros/scan_fine.mac listo para `./hodoscope scan_fine.mac`.

Notas físicas:
- Para resolución sub-mm hay que tomar dx <= 0.3 mm en la zona de overlap.
- 100 muones por punto da una incertidumbre relativa de ~10% en el conteo
  de coincidencias por píxel — suficiente para sanity checks; subir a
  1000 para análisis cuantitativo.
"""

import argparse
import numpy as np
from pathlib import Path

def build(args):
    xs = np.arange(args.xmin, args.xmax + 1e-9, args.dx)
    ys = np.arange(args.ymin, args.ymax + 1e-9, args.dy)

    lines = [
        "# scan_fine.mac — generado por analysis/build_scan_macro.py",
        f"# Grilla: X={len(xs)} pts en [{args.xmin}, {args.xmax}] mm, dx={args.dx}",
        f"#         Y={len(ys)} pts en [{args.ymin}, {args.ymax}] mm, dy={args.dy}",
        f"#         N por punto = {args.n}",
        f"# Total eventos = {len(xs)*len(ys)*args.n}",
        "",
        "/run/initialize",
        "",
        "/hodoscope/det/setD 5.0 mm",
        "/hodoscope/det/optical false",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "",
    ]

    for y in ys:
        for x in xs:
            lines.append(f"/gun/position {x:.3f} {y:.3f} 50.0 mm")
            lines.append(f"/run/beamOn {args.n}")

    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n")
    print(f"[OK] {len(xs)*len(ys)} puntos × {args.n} = "
          f"{len(xs)*len(ys)*args.n} eventos -> {out}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--xmin", type=float, default=-15.0)
    p.add_argument("--xmax", type=float, default= 15.0)
    p.add_argument("--dx",   type=float, default=  0.5)
    p.add_argument("--ymin", type=float, default=-15.0)
    p.add_argument("--ymax", type=float, default= 15.0)
    p.add_argument("--dy",   type=float, default=  0.5)
    p.add_argument("--n",    type=int,   default=100)
    p.add_argument("--energy", type=float, default=4.0,
                   help="Energía cinética del muón en GeV")
    p.add_argument("--out",  type=str,   default="macros/scan_fine.mac")
    build(p.parse_args())
