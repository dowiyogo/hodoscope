#!/usr/bin/env python3.12
"""Estimate accepted muon rate with a simple angular flux model."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from common import EDEP_BRANCHES, NPH_BRANCHES, OUTDIR, TABLE_DIR, VARIANT_LABELS, VARIANT_ROOTS, ensure_dirs, fmt, get_numpy, read_hodo_arrays, write_csv


def flux_weight(theta: float, model: str) -> float:
    if model == "flat":
        return 1.0
    return max(math.cos(theta), 0.0) ** 2


def integrate_flux(theta_max_deg: float, flux_model: str, area_mm2: float) -> float:
    theta_max = math.radians(theta_max_deg)
    n_theta = 240
    n_phi = 360
    dtheta = theta_max / n_theta
    dphi = 2.0 * math.pi / n_phi
    total = 0.0
    for i in range(n_theta):
        theta = (i + 0.5) * dtheta
        for _ in range(n_phi):
            total += flux_weight(theta, flux_model) * math.sin(theta) * dtheta * dphi
    return total * (area_mm2 * 1e-6)


def efficiency_from_root(root_path: Path, threshold_nph: float) -> tuple[float, float]:
    np = get_numpy()
    arrays = read_hodo_arrays(root_path, [*NPH_BRANCHES, *EDEP_BRANCHES])
    nph = np.vstack([arrays[name] for name in NPH_BRANCHES]).T
    edep = np.vstack([arrays[name] for name in EDEP_BRANCHES]).T
    detected = (nph[:, 0:16] >= threshold_nph).any(axis=1) & (
        nph[:, 16:32] >= threshold_nph
    ).any(axis=1)
    return (
        float(detected.mean()) if detected.size else 0.0,
        float(nph.sum(axis=1).mean()) if nph.size else 0.0,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flux-model", choices=["cos2", "flat", "csv"], default="cos2")
    parser.add_argument("--flux-csv", type=Path)
    parser.add_argument("--area-mm2", type=float, default=33 * 33)
    parser.add_argument("--theta-max-deg", type=float, default=60.0)
    parser.add_argument("--threshold-nph", type=float, default=1.0)
    parser.add_argument("--variant", choices=["tio2", "vikuiti", "both"], default="both")
    parser.add_argument("--efficiency-map", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    if args.flux_model == "csv":
        raise RuntimeError("CSV angular flux import is reserved for MuYSC/Meiga tables in a later pass.")
    ideal_rate = integrate_flux(args.theta_max_deg, args.flux_model, args.area_mm2)
    variants = ["tio2", "vikuiti"] if args.variant == "both" else [args.variant]
    rows: list[dict[str, object]] = []
    for variant in variants:
        eff, mean_nph = efficiency_from_root(VARIANT_ROOTS[variant], args.threshold_nph)
        rows.append(
            {
                "variant": variant,
                "variant_label": VARIANT_LABELS[variant],
                "flux_model": args.flux_model,
                "area_mm2": fmt(args.area_mm2),
                "theta_max_deg": fmt(args.theta_max_deg),
                "threshold_nph": fmt(args.threshold_nph),
                "geometric_ideal_rate_arb": fmt(ideal_rate),
                "efficiency": fmt(eff),
                "effective_rate_arb": fmt(ideal_rate * eff),
                "mean_nph_total": fmt(mean_nph),
            }
        )
    columns = list(rows[0].keys())
    write_csv(TABLE_DIR / "accepted_muon_rate_estimate.csv", rows, columns)

    lines = [
        "# Accepted muon rate estimate",
        "",
        f"- Flux model: `{args.flux_model}`",
        f"- Theta max: `{args.theta_max_deg} deg`",
        f"- Area: `{args.area_mm2} mm2`",
        f"- nph threshold: `{args.threshold_nph}`",
        "",
        "| Variant | Ideal rate [arb.] | Efficiency | Effective rate [arb.] |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant_label']} | {row['geometric_ideal_rate_arb']} | "
            f"{row['efficiency']} | {row['effective_rate_arb']} |"
        )
    lines.extend(
        [
            "",
            "This first version uses a simple angular flux model. Production rates should replace this with an angular flux table from MuYSC/Meiga and a detector-specific acceptance matrix.",
        ]
    )
    (OUTDIR / "accepted_muon_rate_estimate.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {TABLE_DIR / 'accepted_muon_rate_estimate.csv'}")
    print(f"Wrote {OUTDIR / 'accepted_muon_rate_estimate.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
