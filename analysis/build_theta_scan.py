#!/usr/bin/env python3
"""
build_theta_scan.py
-------------------

Genera un macro Geant4 para el barrido angular (iteración 0.6).

Diseño:
- Loop externo sobre D ∈ {3.0, 5.0, 8.0} mm.
- Loop interno sobre θ_true ∈ {0, 5, 10, 15, 20} mrad.
- N = 2000 muones por (D, θ) desde posición fija (0, 0, 50) mm.
- Total: 3 × 5 × 2000 = 30 000 eventos.  beamOn calls: 15.
- Cada (D, θ) → archivo theta_scan_D{D}_th{theta_mrad}.root
  (Gotcha G2: extensión .root siempre explícita en setFileName).

Dirección del muón para inclinación θ en plano XZ:
  /gun/direction sin(θ)  0  −cos(θ)
  Para θ=0 se escribe 0.000000 0.0 -1.000000 (exacto).

Uso típico:
    python analysis/build_theta_scan.py
    cd build && ./hodoscope ../macros_generados/theta_scan.mac
    root -l '../analysis/theta_scan_analysis.C("theta_scan_D*_th*.root")'
"""

import argparse
import math
from pathlib import Path

DEFAULT_D_VALUES    = [3.0, 5.0, 8.0]
DEFAULT_THETA_MRAD  = [0, 5, 10, 15, 20]


def build(args):
    Ds          = args.D_values
    thetas_mrad = args.theta_values
    N           = args.n
    n_D         = len(Ds)
    n_th        = len(thetas_mrad)
    n_total     = n_D * n_th * N

    header = [
        "# theta_scan.mac  -  generado por analysis/build_theta_scan.py",
        f"# D ∈ {Ds} mm",
        f"# θ_true ∈ {thetas_mrad} mrad",
        f"# N muones por (D, θ): {N}",
        f"# Total eventos: {n_total}   (beamOn calls: {n_D * n_th})",
        "",
        "/run/initialize",
        "",
        "/gun/particle mu-",
        f"/gun/energy {args.energy} GeV",
        "/gun/position 0.0 0.0 50.0 mm",
        "",
        "/run/printProgress 500",
        "",
    ]

    body = []
    for D in Ds:
        D_str = f"{D:.1f}"
        for theta_mrad in thetas_mrad:
            theta_rad = theta_mrad * 1e-3
            nx = math.sin(theta_rad)   # inclinación en plano XZ
            nz = -math.cos(theta_rad)  # siempre descendente (−Z)
            fname = f"theta_scan_D{D_str}_th{int(theta_mrad)}.root"
            body += [
                f"# ---- D = {D_str} mm, θ = {theta_mrad} mrad " + "-" * 30,
                f"/analysis/setFileName {fname}",
                f"/hodoscope/det/setD {D_str} mm",
                f"/gun/direction {nx:.6f} 0.0 {nz:.6f}",
                f"/run/beamOn {N}",
                "",
            ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(header + body) + "\n")

    n_beamon = n_D * n_th
    print(f"[OK] {n_D} D × {n_th} θ × {N} muones = {n_total} eventos")
    print(f"     /run/beamOn calls: {n_beamon}  (debe ser {n_D} × {n_th} = {n_beamon})")
    print(f"     Macro escrito en: {out}")
    print()
    print("Para correr el barrido:")
    print(f"  cd build && ./hodoscope ../{out}")
    print()
    print("Para analizar (desde build/):")
    print('  root -l \'../analysis/theta_scan_analysis.C("theta_scan_D*_th*.root")\'')


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--D-values", type=float, nargs="+", default=DEFAULT_D_VALUES,
                   dest="D_values",
                   help=f"Valores de D [mm]  (default: {DEFAULT_D_VALUES})")
    p.add_argument("--theta-values", type=float, nargs="+", default=DEFAULT_THETA_MRAD,
                   dest="theta_values",
                   help=f"Valores de θ_true [mrad]  (default: {DEFAULT_THETA_MRAD})")
    p.add_argument("--n",      type=int,   default=2000,
                   help="Muones por (D, θ)  (default: 2000)")
    p.add_argument("--energy", type=float, default=4.0,
                   help="Energía cinética del muón [GeV]  (default: 4.0)")
    p.add_argument("--out",    type=str,
                   default="macros_generados/theta_scan.mac",
                   help="Ruta de salida  (default: macros_generados/theta_scan.mac)")
    build(p.parse_args())
