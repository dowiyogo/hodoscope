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
import uproot


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def rms(values):
    if not values:
        return float("nan")
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / len(values))


def safe_name(base, index):
    return f"{base}_{index:02d}"


def main():
    parser = argparse.ArgumentParser(description="Summarize edep, active bars, dominant bar and first-hit time.")
    parser.add_argument("root_file")
    parser.add_argument("--tree", default="hodo")
    parser.add_argument("--tag", default="run")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    root_file = Path(args.root_file)
    out_dir = Path(args.out_dir)
    table_dir = out_dir / "tables"
    fig_dir = out_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    with uproot.open(root_file) as f:
        if args.tree not in f:
            raise SystemExit(f"Tree {args.tree} not found in {root_file}")
        tree = f[args.tree]
        branches = list(tree.keys())
    edep_names = [safe_name("edep", i) for i in range(32)]
    tfirst_names = [safe_name("tfirst", i) for i in range(32)]
    missing = [name for name in edep_names + tfirst_names if name not in branches]
    if missing:
        raise SystemExit(f"Missing expected branches: {', '.join(missing)}")

    arrays = tree.arrays(["eventID", "prim_x", "prim_y", *edep_names, *tfirst_names], library="np")
    entries = len(arrays["eventID"])

    event_rows = []
    total_edep_values = []
    active_bar_values = []
    first_hit_values = []
    dominant_bar_values = []
    dominant_counts = [0] * 32

    for event_index in range(entries):
        event_id = int(arrays["eventID"][event_index])
        prim_x = float(arrays["prim_x"][event_index])
        prim_y = float(arrays["prim_y"][event_index])

        edep = [float(arrays[name][event_index]) for name in edep_names]
        tfirst = [float(arrays[name][event_index]) for name in tfirst_names]

        total_edep = sum(edep)
        active_bars = sum(1 for value in edep if value > 0.0)
        dominant_bar = max(range(32), key=lambda idx: edep[idx]) if total_edep > 0.0 else -1
        dominant_edep = edep[dominant_bar] if dominant_bar >= 0 else 0.0

        hit_times = [tfirst[idx] for idx, value in enumerate(edep) if value > 0.0 and tfirst[idx] > 0.0]
        first_hit_time = min(hit_times) if hit_times else float("nan")

        if dominant_bar >= 0:
            dominant_counts[dominant_bar] += 1

        total_edep_values.append(total_edep)
        active_bar_values.append(active_bars)
        dominant_bar_values.append(dominant_bar)
        if math.isfinite(first_hit_time):
            first_hit_values.append(first_hit_time)

        event_rows.append({
            "eventID": event_id,
            "prim_x_mm": prim_x,
            "prim_y_mm": prim_y,
            "total_edep_MeV": total_edep,
            "active_bars": active_bars,
            "dominant_bar": dominant_bar,
            "dominant_edep_MeV": dominant_edep,
            "first_hit_time_ns": first_hit_time,
        })

    csv_path = table_dir / f"{args.tag}_event_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(event_rows[0].keys()) if event_rows else [
            "eventID", "prim_x_mm", "prim_y_mm", "total_edep_MeV", "active_bars", "dominant_bar", "dominant_edep_MeV", "first_hit_time_ns"
        ])
        writer.writeheader()
        writer.writerows(event_rows)

    summary = {
        "tag": args.tag,
        "file": str(root_file),
        "tree": args.tree,
        "entries": entries,
        "branches": branches,
        "metrics": {
            "mean_total_edep_MeV": mean(total_edep_values),
            "rms_total_edep_MeV": rms(total_edep_values),
            "mean_active_bars": mean(active_bar_values),
            "rms_active_bars": rms(active_bar_values),
            "fraction_events_with_edep_gt0": sum(1 for value in total_edep_values if value > 0.0) / entries if entries else float("nan"),
            "mean_first_hit_time_ns": mean(first_hit_values),
            "rms_first_hit_time_ns": rms(first_hit_values),
            "dominant_bar_mode": max(range(32), key=lambda idx: dominant_counts[idx]) if entries else -1,
            "dominant_bar_fraction": max(dominant_counts) / entries if entries else float("nan"),
            "dominant_bar_histogram": dominant_counts,
            "active_bar_histogram": [sum(1 for value in active_bar_values if value == idx) for idx in range(33)],
        },
    }

    json_path = table_dir / f"{args.tag}_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_path = table_dir / f"{args.tag}_summary.md"
    top_dominant = sorted(((count, idx) for idx, count in enumerate(dominant_counts)), reverse=True)[:5]
    lines = [
        f"# Edep summary: {args.tag}",
        "",
        f"- File: `{root_file}`",
        f"- Tree: `{args.tree}`",
        f"- Events: `{entries}`",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Mean total edep [MeV] | {summary['metrics']['mean_total_edep_MeV']:.6f} |",
        f"| RMS total edep [MeV] | {summary['metrics']['rms_total_edep_MeV']:.6f} |",
        f"| Mean active bars | {summary['metrics']['mean_active_bars']:.3f} |",
        f"| RMS active bars | {summary['metrics']['rms_active_bars']:.3f} |",
        f"| Fraction events with edep > 0 | {summary['metrics']['fraction_events_with_edep_gt0']:.4f} |",
        f"| Mean first-hit time [ns] | {summary['metrics']['mean_first_hit_time_ns']:.6f} |",
        f"| RMS first-hit time [ns] | {summary['metrics']['rms_first_hit_time_ns']:.6f} |",
        f"| Dominant bar mode | {summary['metrics']['dominant_bar_mode']} |",
        f"| Dominant bar fraction | {summary['metrics']['dominant_bar_fraction']:.4f} |",
        "",
        "## Most frequent dominant bars",
        "",
    ]
    for count, idx in top_dominant:
        lines.append(f"- Bar {idx}: {count} events")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.ravel()
    axes[0].hist(total_edep_values, bins=80, color="#1f77b4", edgecolor="black")
    axes[0].set_title("Total edep")
    axes[0].set_xlabel("Total edep [MeV]")
    axes[0].set_ylabel("Events")
    axes[1].hist(active_bar_values, bins=np.arange(-0.5, 33.5, 1.0), color="#2ca02c", edgecolor="black")
    axes[1].set_title("Active bars")
    axes[1].set_xlabel("Bars with edep > 0")
    axes[1].set_ylabel("Events")
    if first_hit_values:
        axes[2].hist(first_hit_values, bins=80, color="#d62728", edgecolor="black")
    axes[2].set_title("First hit time")
    axes[2].set_xlabel("Time [ns]")
    axes[2].set_ylabel("Events")
    axes[3].bar(np.arange(32), dominant_counts, color="#ff7f0e", edgecolor="black")
    axes[3].set_title("Dominant bar")
    axes[3].set_xlabel("Bar index")
    axes[3].set_ylabel("Events")
    axes[3].set_xticks(np.arange(0, 32, 4))
    fig.tight_layout()
    fig.savefig(fig_dir / f"{args.tag}_summary.png", dpi=160)
    plt.close(fig)

    print(f"[summarize_edep] wrote {csv_path}")
    print(f"[summarize_edep] wrote {json_path}")
    print(f"[summarize_edep] wrote {md_path}")


if __name__ == "__main__":
    main()
