#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fmt(value, digits=6):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def main():
    parser = argparse.ArgumentParser(description="Build the final Iteration 0 validation summary.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--geant4-version", required=True)
    parser.add_argument("--tree-json", required=True)
    parser.add_argument("--summary-json", action="append", default=[])
    parser.add_argument("--comparison-json", action="append", default=[])
    args = parser.parse_args()

    tree = load_json(args.tree_json)
    summaries = [load_json(path) for path in args.summary_json]
    comparisons = [load_json(path) for path in args.comparison_json]

    total_events = sum(summary["entries"] for summary in summaries)
    root_files = len(summaries)
    branch_names = [branch["name"] for branch in tree["branches"]]
    branch_text = ", ".join(branch_names)

    warnings = []
    for comparison in comparisons:
        if not comparison.get("compatible", False):
            warnings.append(f"{comparison['tag']} ST/MT comparison did not pass the default compatibility cuts.")
    if tree["actual_counts"] != tree["expected_counts"]:
        warnings.append("The ROOT tree structure does not match the expected branch counts exactly.")
    if not warnings:
        warnings.append("No structural or statistical warnings were detected by the default checks.")

    lines = [
        "# Iteration 0 Validation Summary",
        "",
        "## Metadata",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Execution date | {args.run_date} |",
        f"| Branch | {args.branch} |",
        f"| Commit | {args.commit} |",
        f"| Geant4 version | {args.geant4_version} |",
        f"| ROOT files generated | {root_files} |",
        f"| Total simulated events | {total_events} |",
        "",
        "## ROOT tree",
        "",
        f"- Tree name: `{tree['tree']}`",
        f"- Entries (reference file): `{tree['entries']}`",
        f"- Branch count: `{tree['n_branches']}`",
        f"- Branches: `{branch_text}`",
        "",
        "## Metrics by run",
        "",
        "| Tag | Entries | Mean edep [MeV] | Active bars | Fraction edep>0 | Mean first-hit [ns] | Dominant bar |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        metrics = summary["metrics"]
        lines.append(
            f"| {summary['tag']} | {summary['entries']} | {fmt(metrics['mean_total_edep_MeV'])} | {fmt(metrics['mean_active_bars'], 3)} | {fmt(metrics['fraction_events_with_edep_gt0'], 4)} | {fmt(metrics['mean_first_hit_time_ns'])} | {metrics['dominant_bar_mode']} |"
        )

    lines += [
        "",
        "## ST vs MT comparison",
        "",
        "| Tag | Same branches | Dominant bar match | Compatible | KS distance total edep | KS distance active bars | KS distance first hit |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for comparison in comparisons:
        lines.append(
            f"| {comparison['tag']} | {str(comparison['same_branches']).lower()} | {str(comparison['dominant_bar_match']).lower()} | {str(comparison['compatible']).lower()} | {fmt(comparison['ks_distance_total_edep'])} | {fmt(comparison['ks_distance_active_bars'])} | {fmt(comparison['ks_distance_first_hit_time'])} |"
        )

    lines += [
        "",
        "## Warnings",
        "",
    ]
    for warning in warnings:
        lines.append(f"- {warning}")

    overall_ok = all(comparison.get("compatible", False) for comparison in comparisons) and tree["actual_counts"] == tree["expected_counts"]
    lines += [
        "",
        "## Conclusion",
        "",
        f"Iteration 0 validation status: {'PASS' if overall_ok else 'REVIEW REQUIRED'}.",
        "",
        "The suite stays within the non-optical Iteration 0 scope and provides a reproducible baseline for the transition to Iteration 1.",
        "",
        "## Files of interest",
        "",
        "- `analysis/iteration0_validation/outputs/root/`",
        "- `analysis/iteration0_validation/outputs/tables/`",
        "- `analysis/iteration0_validation/outputs/figures/`",
        "- `analysis/iteration0_validation/outputs/logs/`",
    ]

    output = Path(args.output)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[make_iteration0_report] wrote {output}")


if __name__ == "__main__":
    main()
