#!/usr/bin/env python3.12
"""Build simplified ideal and effective angular acceptance matrices."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from common import NPH_BRANCHES, OUTDIR, TABLE_DIR, VARIANT_LABELS, VARIANT_ROOTS, ensure_dirs, fmt, get_numpy, read_hodo_arrays, write_csv


def variant_efficiency(variant: str, threshold_nph: float) -> float:
    np = get_numpy()
    arrays = read_hodo_arrays(VARIANT_ROOTS[variant], NPH_BRANCHES)
    nph = np.vstack([arrays[name] for name in NPH_BRANCHES]).T
    detected = (nph[:, 0:16] >= threshold_nph).any(axis=1) & (
        nph[:, 16:32] >= threshold_nph
    ).any(axis=1)
    return float(detected.mean()) if detected.size else 0.0


def matrix_rows(theta_bins: int, phi_bins: int, theta_max_deg: float, threshold_nph: float, variant: str | None) -> list[dict[str, object]]:
    theta_max = math.radians(theta_max_deg)
    dtheta = theta_max / theta_bins
    dphi = 2.0 * math.pi / phi_bins
    efficiency = 1.0 if variant is None else variant_efficiency(variant, threshold_nph)
    rows: list[dict[str, object]] = []
    for itheta in range(theta_bins):
        theta_low = itheta * dtheta
        theta_high = (itheta + 1) * dtheta
        theta_center = 0.5 * (theta_low + theta_high)
        solid_angle = (math.cos(theta_low) - math.cos(theta_high)) * dphi
        geometric = max(math.cos(theta_center), 0.0) * solid_angle
        for iphi in range(phi_bins):
            phi_center = (iphi + 0.5) * dphi
            rows.append(
                {
                    "theta_bin": itheta,
                    "phi_bin": iphi,
                    "theta_center_deg": fmt(math.degrees(theta_center)),
                    "phi_center_deg": fmt(math.degrees(phi_center)),
                    "solid_angle_sr": fmt(solid_angle),
                    "geometric_acceptance": fmt(geometric),
                    "efficiency": fmt(efficiency),
                    "effective_acceptance": fmt(geometric * efficiency),
                    "threshold_nph": fmt(threshold_nph),
                    "variant": "ideal" if variant is None else variant,
                }
            )
    return rows


def write_npz(theta_bins: int, phi_bins: int, ideal_rows: list[dict[str, object]], effective: dict[str, list[dict[str, object]]]) -> None:
    np = get_numpy()
    path = TABLE_DIR / "angular_acceptance_matrices.npz"
    arrays = {
        "ideal": np.asarray([float(row["effective_acceptance"]) for row in ideal_rows]).reshape(theta_bins, phi_bins)
    }
    for variant, rows in effective.items():
        arrays[f"effective_{variant}"] = np.asarray(
            [float(row["effective_acceptance"]) for row in rows]
        ).reshape(theta_bins, phi_bins)
    np.savez(path, **arrays)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theta-bins", type=int, default=12)
    parser.add_argument("--phi-bins", type=int, default=24)
    parser.add_argument("--theta-max-deg", type=float, default=60.0)
    parser.add_argument("--threshold-nph", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    ideal = matrix_rows(args.theta_bins, args.phi_bins, args.theta_max_deg, args.threshold_nph, None)
    columns = list(ideal[0].keys())
    write_csv(TABLE_DIR / "angular_acceptance_ideal.csv", ideal, columns)
    effective = {}
    for variant in ["tio2", "vikuiti"]:
        rows = matrix_rows(args.theta_bins, args.phi_bins, args.theta_max_deg, args.threshold_nph, variant)
        effective[variant] = rows
        write_csv(TABLE_DIR / f"angular_acceptance_effective_{variant}.csv", rows, columns)
    write_npz(args.theta_bins, args.phi_bins, ideal, effective)

    lines = [
        "# Acceptance matrix summary",
        "",
        "The ideal matrix contains a simplified angular geometric acceptance proportional to `cos(theta) dOmega`. The effective matrices multiply the ideal term by the scan-derived detection efficiency for each detector variant and threshold.",
        "",
        f"- theta bins: `{args.theta_bins}`",
        f"- phi bins: `{args.phi_bins}`",
        f"- theta max: `{args.theta_max_deg} deg`",
        f"- threshold nph: `{args.threshold_nph}`",
        "",
        "| Variant | Efficiency applied |",
        "|---|---:|",
    ]
    for variant, rows in effective.items():
        lines.append(f"| {VARIANT_LABELS[variant]} | {rows[0]['efficiency']} |")
    lines.extend(
        [
            "",
            "This is not yet the voxelized inversion matrix `F`. It is an angular response product that can be consumed by later Meiga/MuYSC coupling to build `F` with realistic flux, geometry, and material paths.",
        ]
    )
    (OUTDIR / "acceptance_matrix_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTDIR / 'acceptance_matrix_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
