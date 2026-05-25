#!/usr/bin/env python3.12
"""Estimate single-module spatial resolution from hodoscope position scans."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    EDEP_BRANCHES,
    FIGURE_DIR,
    NPH_BRANCHES,
    OUTDIR,
    TABLE_DIR,
    VARIANT_LABELS,
    VARIANT_ROOTS,
    channel_centers,
    ensure_dirs,
    fmt,
    get_matplotlib_pyplot,
    get_numpy,
    read_hodo_arrays,
    robust_stats,
    weighted_reco,
    write_csv,
)


def variant_from_path(path: Path) -> str:
    name = path.name.lower()
    if "vikuiti" in name:
        return "vikuiti"
    return "tio2"


def stack_channels(arrays: dict[str, object], branches: list[str]):
    np = get_numpy()
    return np.vstack([arrays[name] for name in branches]).T


def residual_figure(path: Path, residuals: object, title: str, xlabel: str) -> None:
    np = get_numpy()
    plt = get_matplotlib_pyplot()
    arr = np.asarray(residuals, dtype=float)
    arr = arr[np.isfinite(arr)]
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4.5))
    if arr.size:
        plt.hist(arr, bins=40, color="#356f8c", alpha=0.85)
        plt.axvline(float(np.mean(arr)), color="#b6423c", linewidth=1.5, label="mean")
        plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("events")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def analyze_file(
    root_path: Path,
    variant: str,
    edep_threshold: float,
    nph_threshold: float,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    np = get_numpy()
    branches = ["prim_x", "prim_y", *EDEP_BRANCHES, *NPH_BRANCHES]
    arrays = read_hodo_arrays(root_path, branches)
    x_true = np.asarray(arrays["prim_x"], dtype=float)
    y_true = np.asarray(arrays["prim_y"], dtype=float)

    edep = stack_channels(arrays, EDEP_BRANCHES)
    nph = stack_channels(arrays, NPH_BRANCHES)
    centers = channel_centers()

    edep_x = edep[:, 0:16]
    edep_y = edep[:, 16:32]
    nph_x = nph[:, 0:16]
    nph_y = nph[:, 16:32]

    x_reco_edep, active_x_edep = weighted_reco(edep_x, centers["x"], edep_threshold)
    y_reco_edep, active_y_edep = weighted_reco(edep_y, centers["y"], edep_threshold)
    x_reco_nph, active_x_nph = weighted_reco(nph_x, centers["x"], nph_threshold)
    y_reco_nph, active_y_nph = weighted_reco(nph_y, centers["y"], nph_threshold)

    residual_sets = {
        ("edep", "x"): x_reco_edep - x_true,
        ("edep", "y"): y_reco_edep - y_true,
        ("nph", "x"): x_reco_nph - x_true,
        ("nph", "y"): y_reco_nph - y_true,
    }
    central = (np.abs(x_true) < 14.0) & (np.abs(y_true) < 14.0)

    rows: list[dict[str, object]] = []
    for (estimator, coord), residuals in residual_sets.items():
        for region, mask in [("all", np.ones_like(central, dtype=bool)), ("central", central)]:
            stats = robust_stats(np.asarray(residuals)[mask])
            rows.append(
                {
                    "variant": variant,
                    "variant_label": VARIANT_LABELS[variant],
                    "estimator": estimator,
                    "coordinate": coord,
                    "region": region,
                    "entries": stats["entries"],
                    "bias_mm": fmt(stats["bias"]),
                    "sigma_mm": fmt(stats["sigma"]),
                    "robust_sigma_mm": fmt(stats["rms_robust"]),
                    "edep_threshold_mev": edep_threshold,
                    "nph_threshold": nph_threshold,
                }
            )

    tag = variant
    residual_figure(
        FIGURE_DIR / f"residual_x_edep_{tag}.png",
        residual_sets[("edep", "x")],
        f"{VARIANT_LABELS[variant]} x residual, edep centroid",
        "x_reco - x_true [mm]",
    )
    residual_figure(
        FIGURE_DIR / f"residual_y_edep_{tag}.png",
        residual_sets[("edep", "y")],
        f"{VARIANT_LABELS[variant]} y residual, edep centroid",
        "y_reco - y_true [mm]",
    )
    residual_figure(
        FIGURE_DIR / f"residual_x_nph_{tag}.png",
        residual_sets[("nph", "x")],
        f"{VARIANT_LABELS[variant]} x residual, nph centroid",
        "x_reco - x_true [mm]",
    )
    residual_figure(
        FIGURE_DIR / f"residual_y_nph_{tag}.png",
        residual_sets[("nph", "y")],
        f"{VARIANT_LABELS[variant]} y residual, nph centroid",
        "y_reco - y_true [mm]",
    )

    details = {
        "variant": variant,
        "entries": int(x_true.size),
        "mean_edep_total": float(edep.sum(axis=1).mean()) if x_true.size else 0.0,
        "mean_nph_total": float(nph.sum(axis=1).mean()) if x_true.size else 0.0,
        "mean_active_x_edep": float(active_x_edep.mean()) if x_true.size else 0.0,
        "mean_active_y_edep": float(active_y_edep.mean()) if x_true.size else 0.0,
        "mean_active_x_nph": float(active_x_nph.mean()) if x_true.size else 0.0,
        "mean_active_y_nph": float(active_y_nph.mean()) if x_true.size else 0.0,
    }
    return rows, details


def write_markdown(rows: list[dict[str, object]], details: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table_lines = [
        "| Variant | Estimator | Coord | Region | Entries | Bias [mm] | Sigma [mm] | Robust sigma [mm] |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        table_lines.append(
            f"| {row['variant_label']} | {row['estimator']} | {row['coordinate']} | "
            f"{row['region']} | {row['entries']} | {row['bias_mm']} | "
            f"{row['sigma_mm']} | {row['robust_sigma_mm']} |"
        )

    detail_lines = [
        "| Variant | Entries | Mean edep total [MeV] | Mean nph total | Mean active X/Y edep | Mean active X/Y nph |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in details:
        detail_lines.append(
            f"| {VARIANT_LABELS[item['variant']]} | {item['entries']} | "
            f"{fmt(item['mean_edep_total'])} | {fmt(item['mean_nph_total'])} | "
            f"{fmt(item['mean_active_x_edep'])}/{fmt(item['mean_active_y_edep'])} | "
            f"{fmt(item['mean_active_x_nph'])}/{fmt(item['mean_active_y_nph'])} |"
        )

    text = [
        "# Spatial resolution summary",
        "",
        "## Method",
        "",
        "This first-pass reconstruction uses the known bar-center geometry and a weighted centroid. Channels `00..15` reconstruct X, and channels `16..31` reconstruct Y. The same centroid is computed once using `edep_NN` weights and once using `nph_NN` weights.",
        "",
        "Upper subplane centers are `-14,-10,-6,-2,2,6,10,14 mm`; lower subplanes are shifted by `+2 mm`. This matches the current single-module geometry and is not a two-module telescope fit.",
        "",
        "The central region uses `|x| < 14 mm` and `|y| < 14 mm` to reduce edge effects from the scan boundary.",
        "",
        "## Event-level signal checks",
        "",
        *detail_lines,
        "",
        "## Resolution table",
        "",
        *table_lines,
        "",
        "## Limitations",
        "",
        "- This is a single-module centroid reconstruction, not a full track fit.",
        "- The `nph` estimator uses ideal optical photons collected by the MPPC volume; it does not include PDE, electronics, dark noise, saturation, cross-talk, afterpulsing, or pulse shape.",
        "- Angular resolution must be estimated parametrically until two complete hodoscopes are simulated together.",
        "",
    ]
    path.write_text("\n".join(text), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tio2", type=Path, default=VARIANT_ROOTS["tio2"])
    parser.add_argument("--vikuiti", type=Path, default=VARIANT_ROOTS["vikuiti"])
    parser.add_argument("--edep-threshold", type=float, default=0.0)
    parser.add_argument("--nph-threshold", type=float, default=0.0)
    parser.add_argument(
        "--csv",
        type=Path,
        default=TABLE_DIR / "spatial_resolution_summary.csv",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=OUTDIR / "spatial_resolution_summary.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    all_rows: list[dict[str, object]] = []
    all_details: list[dict[str, object]] = []
    for variant, path in [("tio2", args.tio2), ("vikuiti", args.vikuiti)]:
        rows, details = analyze_file(path, variant, args.edep_threshold, args.nph_threshold)
        all_rows.extend(rows)
        all_details.append(details)

    columns = [
        "variant",
        "variant_label",
        "estimator",
        "coordinate",
        "region",
        "entries",
        "bias_mm",
        "sigma_mm",
        "robust_sigma_mm",
        "edep_threshold_mev",
        "nph_threshold",
    ]
    write_csv(args.csv, all_rows, columns)
    write_markdown(all_rows, all_details, args.markdown)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
