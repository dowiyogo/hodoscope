#!/usr/bin/env python3
"""
build_d_scan.py
---------------

Genera un macro Geant4 para barrer la separación entre planos D y medir
cómo cambia la resolución espacial reconstruida σ_x(D) y la distribución
de topologías.

Diseño:
- Loop externo sobre D ∈ [dmin, dmax] mm con paso dD → 11 valores por defecto.
- Loop interno sobre x ∈ [xmin, xmax] mm con paso dx → 25 puntos.
- N muones MIP a 4 GeV por punto (vertical, dirección -Z).
- Total por D: 25 × 100 = 2 500 eventos.  Total scan: 11 × 2 500 = 27 500 eventos.
- Cada D escribe a un archivo ROOT separado: d_scan_D{val}.root.
  El ciclado de archivo lo maneja RunAction al detectar el cambio de nombre.

Predicciones analíticas:
  σ_x (overlap, top. 3) ≈ d_eff/√12 ≈ 0.289 mm  — independiente de D.
  σ_θ ≈ d/D (resolución angular) — depende fuertemente de D.
  f_overlap  ≈ constante (geometría intra-plano, no depende de D).
  f_delta    → leve aumento con D (más material y aire entre planos).

Uso típico:
    python analysis/build_d_scan.py
    cd build && ./hodoscope ../macros_generados/d_scan.mac
    root -l '../analysis/d_scan_analysis.C("d_scan_D*.root")'
"""

import argparse
import numpy as np
from pathlib import Path


def build(args):
    Ds = np.arange(args.dmin, args.dmax + 1e-9, args.dD)
    xs = np.arange(args.xmin, args.xmax + 1e-9, args.dx)

    n_D     = len(Ds)
    n_x     = len(xs)
    n_total = n_D * n_x * args.n

    header = [
        "# d_scan.mac  -  generado por analysis/build_d_scan.py",
        f"# Barrido D ∈ [{args.dmin}, {args.dmax}] mm, dD = {args.dD} mm  →  {n_D} valores de D",
        f"# Barrido X ∈ [{args.xmin}, {args.xmax}] mm, dx = {args.dx} mm  →  {n_x} puntos",
        f"# N muones por punto: {args.n}",
        f"# Total eventos: {n_total}   (beamOn calls: {n_D * n_x})",
        f"# Energía: {args.energy} GeV",
        "",
        "/run/initialize",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "",
        "/run/printProgress 500",
        "",
    ]

    body = []
    for D in Ds:
        D_str = f"{D:.1f}"
        # Nota: la extensión .root es obligatoria. Geant4 parsea la extensión
        # del filename para detectar el tipo; sin ella, ".0" o ".5" en
        # "d_scan_D3.0" serían interpretados como tipo desconocido → error.
        body += [
            f"# ---- D = {D_str} mm " + "-" * 40,
            f"/analysis/setFileName d_scan_D{D_str}.root",
            f"/hodoscope/det/setD {D_str} mm",
            "",
        ]
        for x in xs:
            body.append(f"/gun/position {x:.4f} {args.y:.4f} 50.0 mm")
            body.append(f"/run/beamOn {args.n}")
        body.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(header + body) + "\n")

    n_beamon = n_D * n_x
    print(f"[OK] D: {n_D} valores × {n_x} puntos × {args.n} muones/punto = {n_total} eventos")
    print(f"     /run/beamOn calls: {n_beamon}  (debe ser {n_D} × {n_x} = {n_D * n_x})")
    print(f"     Macro escrito en: {out}")
    print()
    print("Para correr el barrido:")
    print(f"  cd build && ./hodoscope ../{out}")
    print()
    print("Para analizar (desde build/):")
    print('  root -l \'../analysis/d_scan_analysis.C("d_scan_D*.root")\'')


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--dmin",   type=float, default=3.0,
                   help="D mínimo [mm]  (default: 3.0)")
    p.add_argument("--dmax",   type=float, default=8.0,
                   help="D máximo [mm]  (default: 8.0)")
    p.add_argument("--dD",     type=float, default=0.5,
                   help="paso en D [mm]  (default: 0.5)")
    p.add_argument("--xmin",   type=float, default=-6.0,
                   help="X mínimo del sub-scan [mm]  (default: -6.0)")
    p.add_argument("--xmax",   type=float, default=+6.0,
                   help="X máximo del sub-scan [mm]  (default: +6.0)")
    p.add_argument("--dx",     type=float, default=0.5,
                   help="paso en X [mm]  (default: 0.5)")
    p.add_argument("--y",      type=float, default=0.0,
                   help="Y fijo [mm]  (default: 0.0)")
    p.add_argument("--n",      type=int,   default=100,
                   help="muones por punto  (default: 100)")
    p.add_argument("--energy", type=float, default=4.0,
                   help="energía cinética del muón [GeV]  (default: 4.0)")
    p.add_argument("--out",    type=str,
                   default="macros_generados/d_scan.mac",
                   help="ruta de salida del macro  (default: macros_generados/d_scan.mac)")
    build(p.parse_args())
