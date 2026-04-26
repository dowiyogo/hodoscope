#!/usr/bin/env python3
"""
build_overlap_zoom.py
---------------------

Escaneo ULTRA-FINO en la zona de overlap entre X-sup y X-inf, centrado
en x = 0 (donde X-inf bar 11 y X-sup bar 4 se solapan en x ∈ [+0.5, +1.5]
y X-inf bar 11 y X-sup bar 3 en x ∈ [-1.5, -0.5]).

Por qué un macro separado:
- En el escaneo grueso (build_x_scan.py, dx=0.2 mm) cada bin tiene 200
  muones, suficiente para ver el diente de sierra a gran escala.
- Para resolver la transición de carga dentro del 1 mm de overlap (el
  "charge sharing" en una iteración futura con óptica activa), hace
  falta dx ≤ 0.05 mm y N ≥ 1000 por punto.
- Esta resolución ya está en el límite de lo medible por simple
  hit-counting; sin óptica, sólo se ve la cuantización geométrica.
  Por eso este macro es preparatorio para la iteración 1 con óptica ON.

Diseño:
- Grilla por defecto: x ∈ [-2, +2] mm, dx = 0.05 mm  → 81 puntos.
- 1000 muones por punto.
- Total: 81 000 eventos. Tiempo serial estimado: ~5 min.

Uso:
    python build_overlap_zoom.py
    cd ../build && ./hodoscope ../overlap_zoom.mac
    root -l '../analysis/x_resolution.C("hodoscope.root", 0.05)'
"""
import argparse
import numpy as np
from pathlib import Path


def build(args):
    xs = np.arange(args.xmin, args.xmax + 1e-9, args.dx)
    header = [
        "# overlap_zoom.mac  -  zona de overlap fino, generado por build_overlap_zoom.py",
        f"# {len(xs)} puntos, dx={args.dx} mm, N={args.n} → {len(xs)*args.n} eventos",
        "",
        "/run/initialize",
        "",
        "/analysis/setFileName overlap_zoom",
        "",
        "/hodoscope/det/setD 5.0 mm",
        "/hodoscope/det/optical false",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "/run/printProgress 5000",
        "",
    ]
    body = []
    for x in xs:
        body.append(f"/gun/position {x:.4f} {args.y:.4f} 50.0 mm")
        body.append(f"/run/beamOn {args.n}")
    Path(args.out).write_text("\n".join(header + body) + "\n")
    print(f"[OK] {len(xs)} pts × {args.n} = {len(xs)*args.n} ev → {args.out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--xmin",   type=float, default=-2.0)
    p.add_argument("--xmax",   type=float, default=+2.0)
    p.add_argument("--dx",     type=float, default= 0.05)
    p.add_argument("--y",      type=float, default= 0.0)
    p.add_argument("--n",      type=int,   default= 1000)
    p.add_argument("--energy", type=float, default= 4.0)
    p.add_argument("--out",    type=str,   default="overlap_zoom.mac")
    build(p.parse_args())
