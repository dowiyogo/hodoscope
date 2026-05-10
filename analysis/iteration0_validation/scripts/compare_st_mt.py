#!/usr/bin/env python3

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def rms(values):
    if not values:
        return float("nan")
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / len(values))


def load_csv(path):
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)
    return rows


def read_values(rows, key, cast=float):
    return [cast(row[key]) for row in rows]


def rel_diff(st, mt):
    denom = 0.5 * (abs(st) + abs(mt))
    if denom == 0.0:
        return 0.0
    return abs(st - mt) / denom


def ks_distance(sample_a, sample_b, bins=60):
    if not sample_a or not sample_b:
        return float("nan")
    lo = min(min(sample_a), min(sample_b))
    hi = max(max(sample_a), max(sample_b))
    if hi == lo:
        return 1.0
    grid = np.linspace(lo, hi, bins + 1)
    hist_a, _ = np.histogram(sample_a, bins=grid)
    hist_b, _ = np.histogram(sample_b, bins=grid)
    cdf_a = np.cumsum(hist_a) / len(sample_a)
    cdf_b = np.cumsum(hist_b) / len(sample_b)
    return float(np.max(np.abs(cdf_a - cdf_b)))


def main():
    parser = argparse.ArgumentParser(description="Compare ST and MT summaries.")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--st-json", required=True)
    parser.add_argument("--mt-json", required=True)
    parser.add_argument("--st-csv", required=True)
    parser.add_argument("--mt-csv", required=True)
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    table_dir = out_dir / "tables"
    fig_dir = out_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    st_summary = json.loads(Path(args.st_json).read_text(encoding="utf-8"))
    mt_summary = json.loads(Path(args.mt_json).read_text(encoding="utf-8"))
    st_rows = load_csv(args.st_csv)
    mt_rows = load_csv(args.mt_csv)

    st_total = read_values(st_rows, "total_edep_MeV")
    mt_total = read_values(mt_rows, "total_edep_MeV")
    st_active = read_values(st_rows, "active_bars", int)
    mt_active = read_values(mt_rows, "active_bars", int)
    st_first = [value for value in read_values(st_rows, "first_hit_time_ns") if math.isfinite(value)]
    mt_first = [value for value in read_values(mt_rows, "first_hit_time_ns") if math.isfinite(value)]

    st_dom = read_values(st_rows, "dominant_bar", int)
    mt_dom = read_values(mt_rows, "dominant_bar", int)

    ks_total = ks_distance(st_total, mt_total)
    ks_active = ks_distance(st_active, mt_active)
    ks_first = ks_distance(st_first, mt_first)

    st_metrics = st_summary["metrics"]
    mt_metrics = mt_summary["metrics"]
    metric_rows = [
        ("entries", st_summary["entries"], mt_summary["entries"]),
        ("mean_total_edep_MeV", st_metrics["mean_total_edep_MeV"], mt_metrics["mean_total_edep_MeV"]),
        ("rms_total_edep_MeV", st_metrics["rms_total_edep_MeV"], mt_metrics["rms_total_edep_MeV"]),
        ("mean_active_bars", st_metrics["mean_active_bars"], mt_metrics["mean_active_bars"]),
        ("rms_active_bars", st_metrics["rms_active_bars"], mt_metrics["rms_active_bars"]),
        ("fraction_events_with_edep_gt0", st_metrics["fraction_events_with_edep_gt0"], mt_metrics["fraction_events_with_edep_gt0"]),
        ("mean_first_hit_time_ns", st_metrics["mean_first_hit_time_ns"], mt_metrics["mean_first_hit_time_ns"]),
        ("rms_first_hit_time_ns", st_metrics["rms_first_hit_time_ns"], mt_metrics["rms_first_hit_time_ns"]),
    ]

    rows = []
    for metric, st_value, mt_value in metric_rows:
        if isinstance(st_value, int) and isinstance(mt_value, int):
            diff = mt_value - st_value
            rel = 0.0 if st_value == mt_value else abs(diff) / max(abs(st_value), abs(mt_value), 1)
        else:
            diff = mt_value - st_value
            rel = rel_diff(st_value, mt_value)
        rows.append({
            "metric": metric,
            "st": st_value,
            "mt": mt_value,
            "abs_diff": diff,
            "rel_diff": rel,
        })

    dominant_match = st_metrics["dominant_bar_mode"] == mt_metrics["dominant_bar_mode"]
    same_branches = st_summary["branches"] == mt_summary["branches"]
    compatible = (
        same_branches
        and rel_diff(st_metrics["mean_total_edep_MeV"], mt_metrics["mean_total_edep_MeV"]) < 0.05
        and rel_diff(st_metrics["mean_active_bars"], mt_metrics["mean_active_bars"]) < 0.10
        and rel_diff(st_metrics["mean_first_hit_time_ns"], mt_metrics["mean_first_hit_time_ns"]) < 0.10
        and ks_total < 0.20
        and ks_active < 0.20
        and ks_first < 0.20
    )

    payload = {
        "tag": args.tag,
        "st_tag": st_summary["tag"],
        "mt_tag": mt_summary["tag"],
        "same_branches": same_branches,
        "dominant_bar_match": dominant_match,
        "ks_distance_total_edep": ks_total,
        "ks_distance_active_bars": ks_active,
        "ks_distance_first_hit_time": ks_first,
        "compatible": compatible,
        "metrics": rows,
    }

    csv_path = table_dir / f"{args.tag}_st_mt_comparison.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "st", "mt", "abs_diff", "rel_diff"])
        writer.writeheader()
        writer.writerows(rows)

    json_path = table_dir / f"{args.tag}_st_mt_comparison.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_path = table_dir / f"{args.tag}_st_mt_comparison.md"
    lines = [
        f"# ST vs MT comparison: {args.tag}",
        "",
        f"- ST tag: `{st_summary['tag']}`",
        f"- MT tag: `{mt_summary['tag']}`",
        f"- Same branches: `{same_branches}`",
        f"- Dominant bar match: `{dominant_match}`",
        f"- Compatible: `{compatible}`",
        f"- KS distance total edep: `{ks_total:.6f}`",
        f"- KS distance active bars: `{ks_active:.6f}`",
        f"- KS distance first hit time: `{ks_first:.6f}`",
        "",
        "| Metric | ST | MT | Abs diff | Rel diff |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['metric']} | {row['st']:.6f} | {row['mt']:.6f} | {row['abs_diff']:.6f} | {row['rel_diff']:.6f} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.ravel()
    axes[0].hist(st_total, bins=60, alpha=0.6, label="ST", color="#1f77b4", edgecolor="black")
    axes[0].hist(mt_total, bins=60, alpha=0.6, label="MT", color="#d62728", edgecolor="black")
    axes[0].set_title("Total edep")
    axes[0].set_xlabel("MeV")
    axes[0].set_ylabel("Events")
    axes[0].legend()

    axes[1].hist(st_active, bins=np.arange(-0.5, 33.5, 1.0), alpha=0.6, label="ST", color="#1f77b4", edgecolor="black")
    axes[1].hist(mt_active, bins=np.arange(-0.5, 33.5, 1.0), alpha=0.6, label="MT", color="#d62728", edgecolor="black")
    axes[1].set_title("Active bars")
    axes[1].set_xlabel("Bars with edep > 0")
    axes[1].set_ylabel("Events")
    axes[1].legend()

    if st_first:
        axes[2].hist(st_first, bins=60, alpha=0.6, label="ST", color="#1f77b4", edgecolor="black")
    if mt_first:
        axes[2].hist(mt_first, bins=60, alpha=0.6, label="MT", color="#d62728", edgecolor="black")
    axes[2].set_title("First hit time")
    axes[2].set_xlabel("ns")
    axes[2].set_ylabel("Events")
    axes[2].legend()

    axes[3].axis("off")
    axes[3].text(0.02, 0.92, f"Same branches: {same_branches}", fontsize=12)
    axes[3].text(0.02, 0.80, f"Dominant bar match: {dominant_match}", fontsize=12)
    axes[3].text(0.02, 0.68, f"Compatible: {compatible}", fontsize=12)
    axes[3].text(0.02, 0.56, f"KS total edep: {ks_total:.4f}", fontsize=12)
    axes[3].text(0.02, 0.44, f"KS active bars: {ks_active:.4f}", fontsize=12)
    axes[3].text(0.02, 0.32, f"KS first hit: {ks_first:.4f}", fontsize=12)
    fig.tight_layout()
    fig.savefig(fig_dir / f"{args.tag}_st_mt_comparison.png", dpi=160)
    plt.close(fig)

    print(f"[compare_st_mt] wrote {csv_path}")
    print(f"[compare_st_mt] wrote {json_path}")
    print(f"[compare_st_mt] wrote {md_path}")


if __name__ == "__main__":
    main()
