#!/usr/bin/env python3.12
"""Evaluate efficiency and relative acceptance versus nph threshold."""

from __future__ import annotations

import argparse

from common import (
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


def analyze_variant(variant: str, thresholds: list[float]) -> list[dict[str, object]]:
    np = get_numpy()
    arrays = read_hodo_arrays(VARIANT_ROOTS[variant], NPH_BRANCHES + ["prim_x", "prim_y"])
    nph = np.vstack([arrays[name] for name in NPH_BRANCHES]).T
    x = np.asarray(arrays["prim_x"], dtype=float)
    y = np.asarray(arrays["prim_y"], dtype=float)
    central = (np.abs(x) <= 14.5) & (np.abs(y) <= 14.5)
    total_nph = nph.sum(axis=1)
    rows: list[dict[str, object]] = []
    baseline_eff = None
    for threshold in thresholds:
        detected = (nph[:, 0:16] >= threshold).any(axis=1) & (
            nph[:, 16:32] >= threshold
        ).any(axis=1)
        eff = float(detected.mean()) if detected.size else 0.0
        central_eff = float(detected[central].mean()) if central.any() else 0.0
        if baseline_eff is None:
            baseline_eff = eff if eff > 0 else 1.0
        mean_accepted_nph = float(total_nph[detected].mean()) if detected.any() else 0.0
        relative_rate = eff / baseline_eff if baseline_eff else 0.0
        rows.append(
            {
                "variant": variant,
                "variant_label": VARIANT_LABELS[variant],
                "threshold_nph": fmt(threshold),
                "efficiency_total": fmt(eff),
                "efficiency_central": fmt(central_eff),
                "mean_accepted_nph": fmt(mean_accepted_nph),
                "relative_effective_acceptance": fmt(relative_rate),
                "relative_expected_counts": fmt(relative_rate),
                "poisson_weight_relative": fmt(1.0 / relative_rate if relative_rate > 0 else float("inf")),
            }
        )
    return rows


def plot_variant(rows: list[dict[str, object]], variant: str) -> None:
    plt = get_matplotlib_pyplot()
    thresholds = [float(row["threshold_nph"]) for row in rows]
    eff = [float(row["efficiency_total"]) for row in rows]
    central = [float(row["efficiency_central"]) for row in rows]
    plt.figure(figsize=(6.5, 4.5))
    plt.plot(thresholds, eff, marker="o", label="total")
    plt.plot(thresholds, central, marker="s", label="central")
    plt.xlabel("nph threshold")
    plt.ylabel("efficiency")
    plt.title(f"{VARIANT_LABELS[variant]} threshold efficiency")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"threshold_efficiency_{variant}.png", dpi=160)
    plt.close()


def plot_comparison(rows: list[dict[str, object]]) -> None:
    plt = get_matplotlib_pyplot()
    plt.figure(figsize=(6.5, 4.5))
    for variant in ["tio2", "vikuiti"]:
        subset = [row for row in rows if row["variant"] == variant]
        thresholds = [float(row["threshold_nph"]) for row in subset]
        rates = [float(row["relative_expected_counts"]) for row in subset]
        plt.plot(thresholds, rates, marker="o", label=VARIANT_LABELS[variant])
    plt.xlabel("nph threshold")
    plt.ylabel("relative expected counts")
    plt.title("Relative rate versus threshold")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "threshold_rate_comparison.png", dpi=160)
    plt.close()


def write_summary(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Threshold sensitivity summary",
        "",
        "This scan evaluates how a simple per-channel `nph` threshold changes detection efficiency, effective acceptance, and relative expected counts.",
        "",
        "| Variant | Threshold | Total eff. | Central eff. | Relative counts | Relative Poisson weight |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant_label']} | {row['threshold_nph']} | "
            f"{row['efficiency_total']} | {row['efficiency_central']} | "
            f"{row['relative_expected_counts']} | {row['poisson_weight_relative']} |"
        )
    lines.extend(
        [
            "",
            "Higher thresholds reduce acceptance and therefore reduce expected counts. In an inversion, this changes Poisson statistical weights approximately as `W proportional to 1 / expected_counts`; bins with lower efficiency need explicit response modeling rather than silent normalization.",
            "",
            "The Vikuiti/ESR variant retains efficiency to higher thresholds because its ideal MPPC-volume photon collection is much larger in the current optical model.",
        ]
    )
    (OUTDIR / "threshold_sensitivity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--thresholds",
        default="1,2,5,10,20,30",
        help="Comma-separated nph thresholds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    thresholds = [float(value) for value in args.thresholds.split(",") if value.strip()]
    rows: list[dict[str, object]] = []
    for variant in ["tio2", "vikuiti"]:
        variant_rows = analyze_variant(variant, thresholds)
        rows.extend(variant_rows)
        plot_variant(variant_rows, variant)
    plot_comparison(rows)
    columns = list(rows[0].keys())
    write_csv(TABLE_DIR / "threshold_sensitivity.csv", rows, columns)
    write_summary(rows)
    print(f"Wrote {TABLE_DIR / 'threshold_sensitivity.csv'}")
    print(f"Wrote {OUTDIR / 'threshold_sensitivity_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
