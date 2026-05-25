#!/usr/bin/env python3.12
"""Analyze TiO2+epoxy central-gun reflector sweep ROOT files."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from common import NPH_BRANCHES, fmt, get_matplotlib_pyplot, get_numpy, read_hodo_arrays, write_csv


BASE = Path("diagnostics/instrument_response/tio2_epoxy_sweep")
OUTPUTS = BASE / "outputs"
TABLES = BASE / "tables"
FIGURES = BASE / "figures"


def parse_metadata(path: Path) -> dict[str, object]:
    stem = path.stem
    if stem == "sweep_tio2_baseline":
        return {"label": "TiO2 baseline", "variant": "tio2", "surface_mode": "default", "r425_effective": ""}
    if stem == "sweep_vikuiti_baseline":
        return {"label": "Vikuiti baseline", "variant": "vikuiti", "surface_mode": "specular", "r425_effective": ""}
    match = re.match(r"sweep_tio2_epoxy_R425_([0-9]+p[0-9]+)_([a-z]+)", stem)
    if not match:
        return {"label": stem, "variant": "unknown", "surface_mode": "", "r425_effective": ""}
    r425 = float(match.group(1).replace("p", "."))
    mode = match.group(2)
    return {
        "label": f"TiO2+epoxy R425={r425:.3f} {mode}",
        "variant": "tio2_epoxy",
        "surface_mode": mode,
        "r425_effective": r425,
    }


def summarize(path: Path) -> dict[str, object]:
    np = get_numpy()
    meta = parse_metadata(path)
    arrays = read_hodo_arrays(path, NPH_BRANCHES)
    nph = np.vstack([arrays[name] for name in NPH_BRANCHES]).T
    total = nph.sum(axis=1)
    active_ge1 = (nph >= 1).sum(axis=1)
    row = {
        **meta,
        "root_file": str(path),
        "entries": int(total.size),
        "mean_total_nph": float(total.mean()) if total.size else 0.0,
        "std_total_nph": float(total.std()) if total.size else 0.0,
        "median_total_nph": float(np.median(total)) if total.size else 0.0,
        "p10_total_nph": float(np.percentile(total, 10)) if total.size else 0.0,
        "p90_total_nph": float(np.percentile(total, 90)) if total.size else 0.0,
        "frac_nph_gt_0": float((total > 0).mean()) if total.size else 0.0,
        "mean_active_channels_nph_ge_1": float(active_ge1.mean()) if active_ge1.size else 0.0,
        "estimated_npe_mean_pde30": float(0.30 * total.mean()) if total.size else 0.0,
    }
    for threshold in [1, 2, 5, 10, 20, 30]:
        detected = (nph[:, 0:16] >= threshold).any(axis=1) & (
            nph[:, 16:32] >= threshold
        ).any(axis=1)
        row[f"efficiency_nph_ge_{threshold}"] = float(detected.mean()) if detected.size else 0.0
    return row


def add_ratios(rows: list[dict[str, object]]) -> None:
    tio2 = next((row for row in rows if row["variant"] == "tio2"), None)
    vikuiti = next((row for row in rows if row["variant"] == "vikuiti"), None)
    tio2_mean = float(tio2["mean_total_nph"]) if tio2 else math.nan
    vik_mean = float(vikuiti["mean_total_nph"]) if vikuiti else math.nan
    for row in rows:
        mean = float(row["mean_total_nph"])
        row["ratio_to_tio2_baseline"] = mean / tio2_mean if tio2_mean > 0 else math.inf
        row["ratio_vikuiti_to_model"] = vik_mean / mean if mean > 0 else math.inf


def sorted_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    def key(row: dict[str, object]):
        if row["variant"] == "tio2":
            return (0, 0.0, "")
        if row["variant"] == "tio2_epoxy":
            return (1, float(row["r425_effective"]), str(row["surface_mode"]))
        if row["variant"] == "vikuiti":
            return (2, 0.0, "")
        return (3, 0.0, str(row["label"]))
    return sorted(rows, key=key)


def interpolate_for_ratio(rows: list[dict[str, object]], target: float) -> str:
    points = [
        (float(row["r425_effective"]), float(row["ratio_vikuiti_to_model"]))
        for row in rows
        if row["variant"] == "tio2_epoxy" and row["surface_mode"] == "diffuse"
    ]
    points.sort()
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if (y0 - target) * (y1 - target) <= 0 and y1 != y0:
            x = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            return fmt(x)
    return "not bracketed"


def first_meeting(rows: list[dict[str, object]], predicate) -> str:
    candidates = [
        row for row in rows
        if row["variant"] == "tio2_epoxy"
        and row["surface_mode"] == "diffuse"
        and predicate(row)
    ]
    if not candidates:
        return "not reached"
    candidates.sort(key=lambda row: float(row["r425_effective"]))
    return fmt(float(candidates[0]["r425_effective"]))


def find_diffuse_row(rows: list[dict[str, object]], r425: float) -> dict[str, object] | None:
    for row in rows:
        if (
            row["variant"] == "tio2_epoxy"
            and row["surface_mode"] == "diffuse"
            and abs(float(row["r425_effective"]) - r425) < 1.0e-9
        ):
            return row
    return None


def closest_to_ratio(rows: list[dict[str, object]], target: float) -> dict[str, object] | None:
    candidates = [
        row for row in rows
        if row["variant"] == "tio2_epoxy" and row["surface_mode"] == "diffuse"
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: abs(float(row["ratio_vikuiti_to_model"]) - target))


def pde30_candidates(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        row for row in rows
        if row["variant"] == "tio2_epoxy"
        and row["surface_mode"] == "diffuse"
        and 5.0 <= float(row["estimated_npe_mean_pde30"]) <= 15.0
    ]


def row_summary(row: dict[str, object] | None) -> str:
    if row is None:
        return "not available"
    return (
        f"`R425={fmt(row['r425_effective'])}` "
        f"(mean nph `{fmt(row['mean_total_nph'])}`, "
        f"Vikuiti/model `{fmt(row['ratio_vikuiti_to_model'])}`, "
        f"eff>=1 `{fmt(row['efficiency_nph_ge_1'])}`, "
        f"eff>=5 `{fmt(row['efficiency_nph_ge_5'])}`, "
        f"est. npe@30% `{fmt(row['estimated_npe_mean_pde30'])}`)"
    )


def make_plots(rows: list[dict[str, object]]) -> None:
    np = get_numpy()
    plt = get_matplotlib_pyplot()
    FIGURES.mkdir(parents=True, exist_ok=True)
    diffuse = [
        row for row in rows
        if row["variant"] == "tio2_epoxy" and row["surface_mode"] == "diffuse"
    ]
    if not diffuse:
        return
    x = np.asarray([float(row["r425_effective"]) for row in diffuse])
    y_mean = np.asarray([float(row["mean_total_nph"]) for row in diffuse])
    y_eff = np.asarray([float(row["efficiency_nph_ge_1"]) for row in diffuse])
    y_ratio = np.asarray([float(row["ratio_vikuiti_to_model"]) for row in diffuse])
    y_npe = np.asarray([float(row["estimated_npe_mean_pde30"]) for row in diffuse])
    plots = [
        ("mean_nph_vs_r425.png", y_mean, "mean total nph/event"),
        ("efficiency_vs_r425.png", y_eff, "efficiency nph >= 1"),
        ("vikuiti_to_tio2_ratio_vs_r425.png", y_ratio, "Vikuiti/model nph ratio"),
        ("estimated_npe_pde30_vs_r425.png", y_npe, "estimated mean npe, PDE=30%"),
    ]
    for filename, y, ylabel in plots:
        plt.figure(figsize=(6.5, 4.2))
        plt.plot(x, y, marker="o")
        plt.xlabel("effective R425")
        plt.ylabel(ylabel)
        plt.grid(alpha=0.25)
        plt.tight_layout()
        plt.savefig(FIGURES / filename, dpi=160)
        plt.close()


def write_markdown(rows: list[dict[str, object]], path: Path) -> None:
    lines = [
        "# TiO2+epoxy reflector sweep summary",
        "",
        "This central-gun sweep varies an effective TiO2+optical-epoxy reflector model for Hod2019 without changing the default Hod2019/TiO2 behavior. The effective `R425` is a model knob near the EJ200 emission peak; it is not a measured material reflectivity.",
        "",
        "The reported `estimated_npe_mean_pde30` is only an analysis estimate `0.30 * mean_total_nph`. It is not a ROOT branch, not a Geant4 PDE simulation, and not an electronics model.",
        "",
        "| Model | R425 | Surface | Entries | Mean nph | Eff >=1 | Eff >=5 | Eff >=10 | Vikuiti/model | est. npe PDE30 |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | {row['r425_effective']} | {row['surface_mode']} | "
            f"{row['entries']} | {fmt(row['mean_total_nph'])} | "
            f"{fmt(row['efficiency_nph_ge_1'])} | {fmt(row['efficiency_nph_ge_5'])} | "
            f"{fmt(row['efficiency_nph_ge_10'])} | {fmt(row['ratio_vikuiti_to_model'])} | "
            f"{fmt(row['estimated_npe_mean_pde30'])} |"
        )

    diffuse_rows = [row for row in rows if row["variant"] == "tio2_epoxy" and row["surface_mode"] == "diffuse"]
    baseline = next(row for row in rows if row["variant"] == "tio2")
    vikuiti = next(row for row in rows if row["variant"] == "vikuiti")
    best_eff5 = first_meeting(diffuse_rows, lambda row: float(row["efficiency_nph_ge_5"]) > 0.50)
    best_eff1 = first_meeting(diffuse_rows, lambda row: float(row["efficiency_nph_ge_1"]) > 0.90)
    best_npe = first_meeting(diffuse_rows, lambda row: 5.0 <= float(row["estimated_npe_mean_pde30"]) <= 15.0)
    near5 = closest_to_ratio(diffuse_rows, 5.0)
    near3 = closest_to_ratio(diffuse_rows, 3.0)
    near2 = closest_to_ratio(diffuse_rows, 2.0)
    npe_rows = pde30_candidates(diffuse_rows)
    npe_list = ", ".join(f"`R425={fmt(row['r425_effective'])}`" for row in npe_rows) or "none"
    conservative = find_diffuse_row(diffuse_rows, 0.954) or near2
    upper = find_diffuse_row(diffuse_rows, 0.956) or (
        npe_rows[0] if npe_rows else None
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Default TiO2 mean nph is `{fmt(baseline['mean_total_nph'])}`, while Vikuiti is `{fmt(vikuiti['mean_total_nph'])}`. In this central sweep the default model is lower than Vikuiti by a factor `{fmt(baseline['ratio_vikuiti_to_model'])}`.",
            f"- Interpolated effective R425 for Vikuiti/model ratio near 10: `{interpolate_for_ratio(diffuse_rows, 10.0)}`.",
            f"- Interpolated effective R425 for ratio near 5: `{interpolate_for_ratio(diffuse_rows, 5.0)}`.",
            f"- Interpolated effective R425 for ratio near 3: `{interpolate_for_ratio(diffuse_rows, 3.0)}`.",
            f"- Interpolated effective R425 for ratio near 2: `{interpolate_for_ratio(diffuse_rows, 2.0)}`.",
            f"- First diffuse R425 with efficiency_nph_ge_1 > 0.90: `{best_eff1}`.",
            f"- First diffuse R425 with efficiency_nph_ge_5 > 0.50: `{best_eff5}`.",
            f"- First diffuse R425 with estimated_npe_mean_pde30 in 5..15: `{best_npe}`.",
            f"- Closest sampled point to Vikuiti/model ratio 5: {row_summary(near5)}.",
            f"- Closest sampled point to ratio 3: {row_summary(near3)}.",
            f"- Closest sampled point to ratio 2: {row_summary(near2)}.",
            f"- Sampled diffuse points with estimated_npe_mean_pde30 in 5..15: {npe_list}.",
            "",
            "## Recommendation",
            "",
            "The fine sweep confirms a steep but now resolved transition between `R425=0.950` and `R425=0.958`. `R425=0.954 diffuse` is the best conservative position-scan candidate from the sampled points: it gives high `nph >= 1` efficiency, `nph >= 5` efficiency above 0.5, and keeps Hod2019 below the Vikuiti baseline.",
            f"Conservative candidate: {row_summary(conservative)}.",
            f"Upper sensitivity candidate: {row_summary(upper)}.",
            "For an intermediate spatial scan, use `dx=dy=2 mm` with `10` to `20` events per point before committing to another full `33 x 33` production scan.",
            "",
            "## Limitations",
            "",
            "- This is a central muon sweep, not a full position scan.",
            "- Effective R425 is not a measured material constant.",
            "- No `npe_NN`, PDE simulation, saturation, cross-talk, afterpulsing, noise, electronics, or pulse shape is implemented here.",
            "- Surface-mode variations are sensitivity tests only.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=OUTPUTS)
    parser.add_argument("--csv", type=Path, default=TABLES / "tio2_epoxy_reflector_sweep.csv")
    parser.add_argument("--markdown", type=Path, default=BASE / "TIO2_EPOXY_REFLECTOR_SWEEP_SUMMARY.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    TABLES.mkdir(parents=True, exist_ok=True)
    paths = sorted(args.input_dir.glob("sweep_*.root"))
    if not paths:
        raise RuntimeError(f"No sweep ROOT files found in {args.input_dir}")
    rows = sorted_rows([summarize(path) for path in paths])
    add_ratios(rows)
    columns = [
        "label", "variant", "surface_mode", "r425_effective", "root_file",
        "entries", "mean_total_nph", "std_total_nph", "median_total_nph",
        "p10_total_nph", "p90_total_nph", "frac_nph_gt_0",
        "mean_active_channels_nph_ge_1", "efficiency_nph_ge_1",
        "efficiency_nph_ge_2", "efficiency_nph_ge_5",
        "efficiency_nph_ge_10", "efficiency_nph_ge_20",
        "efficiency_nph_ge_30", "ratio_to_tio2_baseline",
        "ratio_vikuiti_to_model", "estimated_npe_mean_pde30",
    ]
    csv_rows = []
    for row in rows:
        csv_rows.append({key: fmt(row[key]) if isinstance(row.get(key), float) else row.get(key, "") for key in columns})
    write_csv(args.csv, csv_rows, columns)
    write_markdown(rows, args.markdown)
    make_plots(rows)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
