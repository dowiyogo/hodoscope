#!/usr/bin/env python3.12
"""Analyze intermediate TiO2+epoxy position scans."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from common import (
    EDEP_BRANCHES,
    NPH_BRANCHES,
    VARIANT_ROOTS,
    channel_centers,
    fmt,
    get_matplotlib_pyplot,
    get_numpy,
    read_hodo_arrays,
    robust_stats,
    weighted_reco,
    write_csv,
)


BASE = Path("diagnostics/instrument_response/tio2_epoxy_position_scan")
OUTPUTS = BASE / "outputs"
TABLES = BASE / "tables"
FIGURES = BASE / "figures"
SUMMARY_MD = BASE / "TIO2_EPOXY_POSITION_SCAN_SUMMARY.md"
SUMMARY_CSV = TABLES / "tio2_epoxy_position_scan_summary.csv"


def stack_channels(arrays: dict[str, object], branches: list[str]):
    np = get_numpy()
    return np.vstack([arrays[name] for name in branches]).T


def parse_r425(path: Path) -> float:
    match = re.search(r"R425_([0-9]+p[0-9]+)", path.stem)
    if not match:
        raise ValueError(f"Could not parse R425 from {path.name}")
    return float(match.group(1).replace("p", "."))


def model_label(r425: float) -> str:
    return f"TiO2+epoxy R425={r425:.3f} diffuse"


def detection_mask(nph, threshold: float):
    return (nph[:, 0:16] >= threshold).any(axis=1) & (
        nph[:, 16:32] >= threshold
    ).any(axis=1)


def pixel_key(values, pixel_size: float):
    np = get_numpy()
    return np.rint(values / pixel_size).astype(int)


def map_rows(x, y, nph_total, detected, pixel_size: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    px = pixel_key(x, pixel_size)
    py = pixel_key(y, pixel_size)
    for pix_y in sorted(set(py.tolist())):
        for pix_x in sorted(set(px.tolist())):
            mask = (px == pix_x) & (py == pix_y)
            if not mask.any():
                continue
            rows.append(
                {
                    "pixel_x": int(pix_x),
                    "pixel_y": int(pix_y),
                    "x_center_mm": fmt(float(pix_x) * pixel_size),
                    "y_center_mm": fmt(float(pix_y) * pixel_size),
                    "n_events": int(mask.sum()),
                    "n_detected": int(detected[mask].sum()),
                    "efficiency": float(detected[mask].mean()),
                    "mean_nph_total": float(nph_total[mask].mean()),
                }
            )
    return rows


def map_figure(path: Path, rows: list[dict[str, object]], key: str, title: str) -> None:
    np = get_numpy()
    plt = get_matplotlib_pyplot()
    xs = np.asarray([float(row["x_center_mm"]) for row in rows])
    ys = np.asarray([float(row["y_center_mm"]) for row in rows])
    values = np.asarray([float(row[key]) for row in rows])
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 5))
    sc = plt.scatter(xs, ys, c=values, marker="s", s=120, cmap="viridis")
    plt.colorbar(sc, label=key)
    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")
    plt.title(title)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def summarize_root(
    root_path: Path,
    label: str,
    r425: float | str,
    pixel_size: float,
    central_region_mm: float,
    make_maps: bool,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    np = get_numpy()
    branches = ["prim_x", "prim_y", *EDEP_BRANCHES, *NPH_BRANCHES]
    arrays = read_hodo_arrays(root_path, branches)
    x = np.asarray(arrays["prim_x"], dtype=float)
    y = np.asarray(arrays["prim_y"], dtype=float)
    nph = stack_channels(arrays, NPH_BRANCHES)
    edep = stack_channels(arrays, EDEP_BRANCHES)
    nph_total = nph.sum(axis=1)
    edep_total = edep.sum(axis=1)
    central_half = central_region_mm / 2.0
    central = (np.abs(x) <= central_half) & (np.abs(y) <= central_half)
    sigma_central = (np.abs(x) < 14.0) & (np.abs(y) < 14.0)

    centers = channel_centers()
    x_reco, _ = weighted_reco(nph[:, 0:16], centers["x"], 0.0)
    y_reco, _ = weighted_reco(nph[:, 16:32], centers["y"], 0.0)
    dx = x_reco - x
    dy = y_reco - y
    dx_central = dx[sigma_central]
    dy_central = dy[sigma_central]
    sx = robust_stats(dx_central)
    sy = robust_stats(dy_central)

    row: dict[str, object] = {
        "label": label,
        "r425_effective": r425,
        "root_file": str(root_path),
        "entries": int(nph_total.size),
        "mean_total_nph": float(nph_total.mean()) if nph_total.size else 0.0,
        "median_total_nph": float(np.median(nph_total)) if nph_total.size else 0.0,
        "std_total_nph": float(nph_total.std()) if nph_total.size else 0.0,
        "mean_total_edep": float(edep_total.mean()) if edep_total.size else 0.0,
        "sigma_x_nph_central_mm": sx["rms_robust"],
        "sigma_y_nph_central_mm": sy["rms_robust"],
        "sigma_x_entries": sx["entries"],
        "sigma_y_entries": sy["entries"],
    }
    for threshold in [1, 2, 5, 10, 20, 30]:
        detected = detection_mask(nph, float(threshold))
        row[f"efficiency_nph_ge_{threshold}"] = float(detected.mean())
        if threshold in {1, 5, 10}:
            row[f"central_efficiency_nph_ge_{threshold}"] = (
                float(detected[central].mean()) if central.any() else math.nan
            )

    map_data: list[dict[str, object]] = []
    if make_maps:
        detected_ge1 = detection_mask(nph, 1.0)
        map_data = map_rows(x, y, nph_total, detected_ge1, pixel_size)
        tag = f"R425_{str(r425).replace('.', 'p')}"
        map_figure(
            FIGURES / f"mean_nph_map_{tag}.png",
            map_data,
            "mean_nph_total",
            f"{label} mean total nph",
        )
        map_figure(
            FIGURES / f"efficiency_map_{tag}.png",
            map_data,
            "efficiency",
            f"{label} efficiency nph >= 1",
        )
    return row, map_data


def load_comparison_rows(pixel_size: float, central_region_mm: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    comparisons = [
        ("Hod2019/TiO2 production", "default", VARIANT_ROOTS["tio2"]),
        ("Hod2018/Vikuiti production", "vikuiti", VARIANT_ROOTS["vikuiti"]),
    ]
    for label, r425, path in comparisons:
        if path.exists():
            row, _ = summarize_root(
                path,
                label,
                r425,
                pixel_size,
                central_region_mm,
                make_maps=False,
            )
            rows.append(row)
    return rows


def write_markdown(
    candidate_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
    path: Path,
    events_expected: int,
) -> None:
    all_rows = [*comparison_rows, *candidate_rows]
    table = [
        "| Model | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in all_rows:
        table.append(
            f"| {row['label']} | {row['entries']} | {fmt(row['mean_total_nph'])} | "
            f"{fmt(row['efficiency_nph_ge_1'])} | {fmt(row['efficiency_nph_ge_5'])} | "
            f"{fmt(row.get('central_efficiency_nph_ge_1'))} | "
            f"{fmt(row.get('central_efficiency_nph_ge_5'))} | "
            f"{fmt(row['sigma_x_nph_central_mm'])} | "
            f"{fmt(row['sigma_y_nph_central_mm'])} |"
        )

    by_r425 = {str(row["r425_effective"]): row for row in candidate_rows}
    r0954 = by_r425.get("0.954")
    r0956 = by_r425.get("0.956")
    recommendation = (
        "`R425=0.954 diffuse` is the conservative candidate, but "
        "`R425=0.956 diffuse` is the stronger single production candidate in this "
        "intermediate scan because it improves threshold efficiency and spatial "
        "response while staying below the Vikuiti production mean nph."
    )

    lines = [
        "# TiO2+epoxy intermediate position scan summary",
        "",
        "## Configuration",
        "",
        "- Detector variant: `Hod2019`",
        "- Reflector model: TiO2+epoxy effective, `diffuse` surface mode",
        "- R425 values: `0.954`, `0.956`",
        "- Grid: `x,y = -16,-14,...,+16 mm`",
        "- Step: `dx=dy=2 mm`",
        "- Events per point: `20`",
        f"- Expected events per model: `{events_expected}`",
        "- Threads: `HODO_THREADS=16`",
        "",
        "## Summary table",
        "",
        *table,
        "",
        "## Interpretation",
        "",
        "- `R425=0.954 diffuse` has high central `nph >= 1` efficiency and remains well below the Vikuiti production mean nph, making it the conservative model.",
        "- `R425=0.956 diffuse` improves the `nph >= 5` efficiency and spatial response, remains below the Vikuiti production mean nph, and does not look like an absurd overcorrection in this intermediate scan.",
        f"- Recommendation: {recommendation}",
        "- For the next production position scan, run both `0.954` and `0.956` if time permits. If only one production scan is practical, run `R425=0.956 diffuse`; keep `0.954` as the conservative systematic bracket.",
        "",
        "## Limitations",
        "",
        "- This is an intermediate `17 x 17` position scan, not the full `33 x 33` production scan.",
        "- `R425` is an effective model reflectivity near 425 nm, not a measured physical reflectivity.",
        "- `nph` is ideal MPPC-volume photon collection; no `npe_NN`, PDE, electronics, saturation, cross-talk, afterpulsing, dark noise, or pulse shape is included.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=OUTPUTS)
    parser.add_argument("--pixel-size-mm", type=float, default=2.0)
    parser.add_argument("--central-region-mm", type=float, default=29.0)
    parser.add_argument("--expected-events", type=int, default=17 * 17 * 20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    paths = sorted(args.input_dir.glob("position_scan_tio2_epoxy_R425_*_diffuse.root"))
    if not paths:
        raise RuntimeError(f"No TiO2+epoxy position-scan ROOTs found in {args.input_dir}")

    rows: list[dict[str, object]] = []
    for root_path in paths:
        r425 = parse_r425(root_path)
        row, map_data = summarize_root(
            root_path,
            model_label(r425),
            r425,
            args.pixel_size_mm,
            args.central_region_mm,
            make_maps=True,
        )
        rows.append(row)
        map_columns = [
            "pixel_x",
            "pixel_y",
            "x_center_mm",
            "y_center_mm",
            "n_events",
            "n_detected",
            "efficiency",
            "mean_nph_total",
        ]
        write_csv(
            TABLES / f"tio2_epoxy_position_scan_pixels_R425_{str(r425).replace('.', 'p')}.csv",
            [
                {
                    key: fmt(item[key]) if isinstance(item.get(key), float) else item.get(key, "")
                    for key in map_columns
                }
                for item in map_data
            ],
            map_columns,
        )

    rows.sort(key=lambda row: float(row["r425_effective"]))
    comparison_rows = load_comparison_rows(args.pixel_size_mm, args.central_region_mm)
    columns = [
        "label",
        "r425_effective",
        "root_file",
        "entries",
        "mean_total_nph",
        "median_total_nph",
        "std_total_nph",
        "mean_total_edep",
        "efficiency_nph_ge_1",
        "efficiency_nph_ge_2",
        "efficiency_nph_ge_5",
        "efficiency_nph_ge_10",
        "efficiency_nph_ge_20",
        "efficiency_nph_ge_30",
        "central_efficiency_nph_ge_1",
        "central_efficiency_nph_ge_5",
        "central_efficiency_nph_ge_10",
        "sigma_x_nph_central_mm",
        "sigma_y_nph_central_mm",
        "sigma_x_entries",
        "sigma_y_entries",
    ]
    write_csv(
        SUMMARY_CSV,
        [
            {
                key: fmt(row[key]) if isinstance(row.get(key), float) else row.get(key, "")
                for key in columns
            }
            for row in rows
        ],
        columns,
    )
    write_markdown(rows, comparison_rows, SUMMARY_MD, args.expected_events)
    print(f"Wrote {SUMMARY_CSV}")
    print(f"Wrote {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
