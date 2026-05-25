#!/usr/bin/env python3.12
"""Build virtual-pixel efficiency maps from position-scan ROOT files."""

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
    ensure_dirs,
    fmt,
    get_matplotlib_pyplot,
    get_numpy,
    read_hodo_arrays,
    write_csv,
)


def stack_channels(arrays: dict[str, object], branches: list[str]):
    np = get_numpy()
    return np.vstack([arrays[name] for name in branches]).T


def pixel_index(values, pixel_size: float):
    np = get_numpy()
    return np.floor(values / pixel_size).astype(int)


def map_figure(path: Path, rows: list[dict[str, object]], value_key: str, title: str) -> None:
    np = get_numpy()
    plt = get_matplotlib_pyplot()
    xs = np.asarray([float(row["x_center_mm"]) for row in rows])
    ys = np.asarray([float(row["y_center_mm"]) for row in rows])
    values = np.asarray([float(row[value_key]) for row in rows])
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 5))
    sc = plt.scatter(xs, ys, c=values, marker="s", s=95, cmap="viridis")
    plt.colorbar(sc, label=value_key)
    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")
    plt.title(title)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def summarize_variant(
    root_path: Path,
    variant: str,
    use: str,
    threshold_nph: float,
    threshold_edep: float,
    pixel_size: float,
    central_region_mm: float,
) -> tuple[list[dict[str, object]], dict[str, float]]:
    np = get_numpy()
    arrays = read_hodo_arrays(root_path, ["prim_x", "prim_y", *EDEP_BRANCHES, *NPH_BRANCHES])
    x = np.asarray(arrays["prim_x"], dtype=float)
    y = np.asarray(arrays["prim_y"], dtype=float)
    edep = stack_channels(arrays, EDEP_BRANCHES)
    nph = stack_channels(arrays, NPH_BRANCHES)

    selected = nph if use == "nph" else edep
    threshold = threshold_nph if use == "nph" else threshold_edep
    active_x = (selected[:, 0:16] >= threshold).any(axis=1)
    active_y = (selected[:, 16:32] >= threshold).any(axis=1)
    detected = active_x & active_y
    active_channels = (selected >= threshold).sum(axis=1)
    edep_total = edep.sum(axis=1)
    nph_total = nph.sum(axis=1)

    px = pixel_index(x, pixel_size)
    py = pixel_index(y, pixel_size)
    rows: list[dict[str, object]] = []
    for pix_x in sorted(set(px.tolist())):
        for pix_y in sorted(set(py.tolist())):
            mask = (px == pix_x) & (py == pix_y)
            if not mask.any():
                continue
            n_events = int(mask.sum())
            n_detected = int(detected[mask].sum())
            rows.append(
                {
                    "pixel_x": pix_x,
                    "pixel_y": pix_y,
                    "x_center_mm": fmt((pix_x + 0.5) * pixel_size),
                    "y_center_mm": fmt((pix_y + 0.5) * pixel_size),
                    "n_events": n_events,
                    "n_detected": n_detected,
                    "efficiency": fmt(n_detected / n_events if n_events else 0.0),
                    "mean_nph_total": fmt(float(nph_total[mask].mean())),
                    "mean_edep_total": fmt(float(edep_total[mask].mean())),
                    "mean_active_channels": fmt(float(active_channels[mask].mean())),
                }
            )

    total_eff = float(detected.mean()) if detected.size else 0.0
    central_half = central_region_mm / 2.0
    central = (np.abs(x) <= central_half) & (np.abs(y) <= central_half)
    central_eff = float(detected[central].mean()) if central.any() else 0.0
    effs = [float(row["efficiency"]) for row in rows]
    metrics = {
        "total_efficiency": total_eff,
        "central_efficiency": central_eff,
        "min_efficiency": min(effs) if effs else 0.0,
        "max_efficiency": max(effs) if effs else 0.0,
        "mean_nph_total": float(nph_total.mean()) if nph_total.size else 0.0,
        "mean_edep_total": float(edep_total.mean()) if edep_total.size else 0.0,
    }

    map_figure(
        FIGURE_DIR / f"efficiency_map_{variant}.png",
        rows,
        "efficiency",
        f"{VARIANT_LABELS[variant]} virtual-pixel efficiency",
    )
    map_figure(
        FIGURE_DIR / f"mean_nph_map_{variant}.png",
        rows,
        "mean_nph_total",
        f"{VARIANT_LABELS[variant]} mean total nph",
    )
    return rows, metrics


def write_summary(path: Path, metrics: dict[str, dict[str, float]], use: str, threshold: float) -> None:
    lines = [
        "# Virtual pixel efficiency summary",
        "",
        f"- Detection observable: `{use}`",
        f"- Per-channel threshold: `{threshold}`",
        "- Event is detected when at least one X channel and at least one Y channel are active.",
        "",
        "| Variant | Total efficiency | Central 29x29 mm2 efficiency | Min pixel eff. | Max pixel eff. | Mean nph total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for variant in ["tio2", "vikuiti"]:
        item = metrics[variant]
        lines.append(
            f"| {VARIANT_LABELS[variant]} | {fmt(item['total_efficiency'])} | "
            f"{fmt(item['central_efficiency'])} | {fmt(item['min_efficiency'])} | "
            f"{fmt(item['max_efficiency'])} | {fmt(item['mean_nph_total'])} |"
        )
    lines.extend(
        [
            "",
            "## Low-efficiency pixels",
            "",
            "Pixels with low efficiency are expected near edges and at threshold values where the idealized optical collection is sparse. These tables are a first format for later acceptance weighting in Meiga/MuYSC workflows.",
            "",
            "## Limitations",
            "",
            "- Uses a scan-generated event sample, not a cosmic angular distribution.",
            "- `nph` is ideal MPPC-volume photon collection and has no real PDE or electronics response yet.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tio2", type=Path, default=VARIANT_ROOTS["tio2"])
    parser.add_argument("--vikuiti", type=Path, default=VARIANT_ROOTS["vikuiti"])
    parser.add_argument("--threshold-nph", type=float, default=1.0)
    parser.add_argument("--threshold-edep", type=float, default=0.0)
    parser.add_argument("--use", choices=["nph", "edep"], default="nph")
    parser.add_argument("--pixel-size-mm", type=float, default=1.0)
    parser.add_argument("--central-region-mm", type=float, default=29.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    columns = [
        "pixel_x",
        "pixel_y",
        "x_center_mm",
        "y_center_mm",
        "n_events",
        "n_detected",
        "efficiency",
        "mean_nph_total",
        "mean_edep_total",
        "mean_active_channels",
    ]
    all_metrics: dict[str, dict[str, float]] = {}
    for variant, path in [("tio2", args.tio2), ("vikuiti", args.vikuiti)]:
        rows, metrics = summarize_variant(
            path,
            variant,
            args.use,
            args.threshold_nph,
            args.threshold_edep,
            args.pixel_size_mm,
            args.central_region_mm,
        )
        write_csv(TABLE_DIR / f"virtual_pixel_efficiency_{variant}.csv", rows, columns)
        all_metrics[variant] = metrics
    threshold = args.threshold_nph if args.use == "nph" else args.threshold_edep
    write_summary(OUTDIR / "virtual_pixel_efficiency_summary.md", all_metrics, args.use, threshold)
    print(f"Wrote {OUTDIR / 'virtual_pixel_efficiency_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
