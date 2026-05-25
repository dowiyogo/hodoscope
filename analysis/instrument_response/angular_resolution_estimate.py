#!/usr/bin/env python3.12
"""Parametric angular-resolution estimate from single-module spatial results."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from common import OUTDIR, TABLE_DIR, VARIANT_LABELS, fmt, read_csv_dicts, write_csv


DEFAULT_BASELINES = [50.0, 100.0, 200.0, 500.0, 1000.0]


def get_sigma(rows: list[dict[str, str]], variant: str, coordinate: str, estimator: str, region: str) -> float:
    candidates = [
        row
        for row in rows
        if row["variant"] == variant
        and row["coordinate"] == coordinate
        and row["estimator"] == estimator
        and row["region"] == region
    ]
    if not candidates:
        raise RuntimeError(f"No spatial sigma for {variant} {estimator} {coordinate} {region}")
    row = candidates[0]
    for key in ["robust_sigma_mm", "sigma_mm"]:
        value = float(row[key])
        if math.isfinite(value):
            return value
    return float("nan")


def write_markdown(path: Path, rows: list[dict[str, object]], estimator: str, region: str) -> None:
    lines = [
        "# Angular resolution estimate",
        "",
        f"- Spatial estimator: `{estimator}`",
        f"- Spatial region: `{region}`",
        "- Method: parametric two-module propagation from single-module spatial resolutions.",
        "",
        "Important: `D` is the internal X/Y plane separation inside one hodoscope module and must not be confused with `L`. `L` is the longitudinal distance between Hodo2018 and Hodo2019, measured between reconstructed active centers of the two complete modules.",
        "",
        "This is not a replacement for a Geant4 simulation with two separated hodoscopes. It is a bridge quantity for connecting module characterization to Meiga/MuYSC acceptance and inversion studies.",
        "",
        "| L [mm] | Pair | sigma theta x [mrad] | sigma theta y [mrad] | Method |",
        "|---:|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['baseline_mm']} | {row['variant_pair']} | "
            f"{row['sigma_theta_x_mrad']} | {row['sigma_theta_y_mrad']} | {row['method']} |"
        )
    lines.extend(
        [
            "",
            "σθ improves approximately as `1/L`. For production studies, MuYSC/Meiga should consume a two-module acceptance model or a full Geant4 telescope response when available.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-mm", type=float, default=100.0)
    parser.add_argument(
        "--spatial-summary",
        type=Path,
        default=TABLE_DIR / "spatial_resolution_summary.csv",
    )
    parser.add_argument("--estimator", choices=["nph", "edep"], default="nph")
    parser.add_argument("--region", choices=["central", "all"], default="central")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baselines = sorted(set([*DEFAULT_BASELINES, args.baseline_mm]))
    spatial_rows = read_csv_dicts(args.spatial_summary)

    sx_2018 = get_sigma(spatial_rows, "vikuiti", "x", args.estimator, args.region)
    sy_2018 = get_sigma(spatial_rows, "vikuiti", "y", args.estimator, args.region)
    sx_2019 = get_sigma(spatial_rows, "tio2", "x", args.estimator, args.region)
    sy_2019 = get_sigma(spatial_rows, "tio2", "y", args.estimator, args.region)

    separate = all(math.isfinite(v) for v in [sx_2018, sy_2018, sx_2019, sy_2019])
    rows: list[dict[str, object]] = []
    for baseline in baselines:
        if separate:
            stx = math.sqrt(sx_2018 * sx_2018 + sx_2019 * sx_2019) / baseline
            sty = math.sqrt(sy_2018 * sy_2018 + sy_2019 * sy_2019) / baseline
            method = "two_module_parametric"
        else:
            sx = sx_2018 if math.isfinite(sx_2018) else sx_2019
            sy = sy_2018 if math.isfinite(sy_2018) else sy_2019
            stx = math.sqrt(2.0) * sx / baseline
            sty = math.sqrt(2.0) * sy / baseline
            method = "equivalent_modules_approx"
        rows.append(
            {
                "baseline_mm": fmt(baseline),
                "variant_pair": "Hod2018/Vikuiti + Hod2019/TiO2",
                "sigma_x_hod2018_mm": fmt(sx_2018),
                "sigma_y_hod2018_mm": fmt(sy_2018),
                "sigma_x_hod2019_mm": fmt(sx_2019),
                "sigma_y_hod2019_mm": fmt(sy_2019),
                "sigma_theta_x_rad": fmt(stx),
                "sigma_theta_y_rad": fmt(sty),
                "sigma_theta_x_mrad": fmt(1000.0 * stx),
                "sigma_theta_y_mrad": fmt(1000.0 * sty),
                "method": method,
            }
        )
    columns = [
        "baseline_mm",
        "variant_pair",
        "sigma_x_hod2018_mm",
        "sigma_y_hod2018_mm",
        "sigma_x_hod2019_mm",
        "sigma_y_hod2019_mm",
        "sigma_theta_x_rad",
        "sigma_theta_y_rad",
        "sigma_theta_x_mrad",
        "sigma_theta_y_mrad",
        "method",
    ]
    write_csv(TABLE_DIR / "angular_resolution_estimate.csv", rows, columns)
    write_markdown(OUTDIR / "angular_resolution_estimate.md", rows, args.estimator, args.region)
    print(f"Wrote {TABLE_DIR / 'angular_resolution_estimate.csv'}")
    print(f"Wrote {OUTDIR / 'angular_resolution_estimate.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
