#!/usr/bin/env python3.12
"""Summarize optical photon collection for the hodoscope variants.

The script reads the `hodo` TTree from the TiO2 and Vikuiti ROOT outputs,
sums `nph_00` ... `nph_31` per event, and writes a comparison CSV and
Markdown report. It prefers uproot and falls back to PyROOT when available.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import math
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CHANNELS = [f"nph_{i:02d}" for i in range(32)]
DEFAULT_TIO2 = Path(
    "diagnostics/optical_variant_comparison/outputs/variant_tio2_quick.root"
)
DEFAULT_VIKUITI = Path(
    "diagnostics/optical_variant_comparison/outputs/variant_vikuiti_quick.root"
)
DEFAULT_CSV = Path("diagnostics/optical_variant_comparison/summary_16threads.csv")
DEFAULT_MD = Path("diagnostics/optical_variant_comparison/summary_16threads.md")
BACKEND_CACHE: tuple[str, object] | None = None


@dataclass
class VariantSummary:
    label: str
    path: Path
    tree_name: str
    entries: int
    mean_total_nph: float
    std_total_nph: float
    median_total_nph: float
    fraction_events_nph_gt_0: float
    mean_active_mppc_channels: float
    channel_means: dict[str, float]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(
            ["git", *args], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return default


def import_uproot() -> tuple[object | None, str | None]:
    try:
        import uproot  # type: ignore

        return uproot, None
    except ImportError as first_error:
        install_cmd = [
            "python3.12",
            "-m",
            "pip",
            "install",
            "--user",
            "uproot",
            "awkward",
            "numpy",
            "pandas",
        ]
        print(
            "uproot is not importable; trying to install Python ROOT-analysis "
            f"dependencies with: {' '.join(install_cmd)}",
            file=sys.stderr,
        )
        install = subprocess.run(install_cmd)
        if install.returncode != 0:
            return None, (
                f"uproot import failed ({first_error}) and automatic install "
                f"failed with exit code {install.returncode}"
            )

        importlib.invalidate_caches()
        try:
            import uproot  # type: ignore

            return uproot, None
        except Exception as second_error:
            return None, (
                f"uproot import failed after automatic install: {second_error}"
            )


def import_pyroot() -> tuple[object | None, str | None]:
    try:
        import ROOT  # type: ignore

        return ROOT, None
    except Exception as error:
        return None, f"PyROOT import failed: {error}"


def select_backend() -> tuple[str, object]:
    global BACKEND_CACHE
    if BACKEND_CACHE is not None:
        return BACKEND_CACHE

    uproot_module, uproot_error = import_uproot()
    if uproot_module is not None:
        BACKEND_CACHE = ("uproot", uproot_module)
        return BACKEND_CACHE

    root_module, root_error = import_pyroot()
    if root_module is not None:
        BACKEND_CACHE = ("PyROOT", root_module)
        return BACKEND_CACHE

    raise RuntimeError(
        "Could not import a ROOT file reader.\n"
        f"- {uproot_error}\n"
        f"- {root_error}\n\n"
        "Install one of the supported Python backends and rerun, for example:\n"
        "  python3.12 -m pip install --user uproot awkward numpy pandas\n"
        "or configure your ROOT environment so `python3.12 -c 'import ROOT'` "
        "works."
    )


def read_with_uproot(
    path: Path, uproot_module: object
) -> tuple[str, dict[str, list[float]]]:
    uproot = uproot_module

    with uproot.open(path) as root_file:
        if "hodo" in root_file:
            tree_name = "hodo"
        else:
            tree_name = ""
            for key, obj in root_file.items():
                if hasattr(obj, "arrays"):
                    tree_name = key.split(";")[0]
                    break
            if not tree_name:
                raise RuntimeError(f"No TTree found in {path}")

        tree = root_file[tree_name]
        missing = [name for name in CHANNELS if name not in tree.keys()]
        if missing:
            raise RuntimeError(f"{path} is missing branches: {', '.join(missing)}")
        arrays = tree.arrays(CHANNELS, library="np")
        return tree_name, {name: arrays[name].tolist() for name in CHANNELS}


def read_with_pyroot(
    path: Path, root_module: object
) -> tuple[str, dict[str, list[float]]]:
    ROOT = root_module
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Could not open {path}")

    tree_name = "hodo" if root_file.Get("hodo") else ""
    if not tree_name:
        keys = root_file.GetListOfKeys()
        for idx in range(keys.GetEntries()):
            key = keys.At(idx)
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.TTree.Class()):
                tree_name = key.GetName()
                break
    if not tree_name:
        raise RuntimeError(f"No TTree found in {path}")

    tree = root_file.Get(tree_name)
    missing = [name for name in CHANNELS if not tree.GetBranch(name)]
    if missing:
        raise RuntimeError(f"{path} is missing branches: {', '.join(missing)}")

    values = {name: [] for name in CHANNELS}
    for entry in tree:
        for name in CHANNELS:
            values[name].append(float(getattr(entry, name)))
    root_file.Close()
    return tree_name, values


def read_channels(path: Path) -> tuple[str, dict[str, list[float]], str]:
    if not path.exists():
        raise FileNotFoundError(path)

    backend, module = select_backend()
    if backend == "uproot":
        tree_name, values = read_with_uproot(path, module)
        return tree_name, values, "uproot"

    tree_name, values = read_with_pyroot(path, module)
    return tree_name, values, "PyROOT"


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def summarize(label: str, path: Path) -> tuple[VariantSummary, str]:
    tree_name, channels, backend = read_channels(path)
    entries = len(channels[CHANNELS[0]])
    totals = [
        sum(channels[channel][idx] for channel in CHANNELS) for idx in range(entries)
    ]
    active_channels = [
        sum(1 for channel in CHANNELS if channels[channel][idx] > 0)
        for idx in range(entries)
    ]
    channel_means = {channel: mean(channels[channel]) for channel in CHANNELS}

    summary = VariantSummary(
        label=label,
        path=path,
        tree_name=tree_name,
        entries=entries,
        mean_total_nph=mean(totals),
        std_total_nph=statistics.pstdev(totals) if entries else 0.0,
        median_total_nph=statistics.median(totals) if entries else 0.0,
        fraction_events_nph_gt_0=(
            sum(1 for value in totals if value > 0) / entries if entries else 0.0
        ),
        mean_active_mppc_channels=mean(active_channels),
        channel_means=channel_means,
    )
    return summary, backend


def fmt(value: float) -> str:
    if math.isinf(value):
        return "inf"
    if math.isnan(value):
        return "nan"
    return f"{value:.6g}"


def write_csv(path: Path, summaries: list[VariantSummary], ratio: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "variant",
        "file",
        "tree",
        "entries",
        "mean_total_nph_per_event",
        "std_total_nph_per_event",
        "median_total_nph_per_event",
        "fraction_events_total_nph_gt_0",
        "mean_active_mppc_channels_per_event",
        "ratio_mean_nph_vikuiti_over_tio2",
        *[f"mean_{channel}" for channel in CHANNELS],
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for summary in summaries:
            row = {
                "variant": summary.label,
                "file": str(summary.path),
                "tree": summary.tree_name,
                "entries": summary.entries,
                "mean_total_nph_per_event": fmt(summary.mean_total_nph),
                "std_total_nph_per_event": fmt(summary.std_total_nph),
                "median_total_nph_per_event": fmt(summary.median_total_nph),
                "fraction_events_total_nph_gt_0": fmt(
                    summary.fraction_events_nph_gt_0
                ),
                "mean_active_mppc_channels_per_event": fmt(
                    summary.mean_active_mppc_channels
                ),
                "ratio_mean_nph_vikuiti_over_tio2": fmt(ratio),
            }
            row.update(
                {
                    f"mean_{channel}": fmt(summary.channel_means[channel])
                    for channel in CHANNELS
                }
            )
            writer.writerow(row)


def markdown_table(summaries: list[VariantSummary]) -> str:
    lines = [
        "| Variante | Entries | Mean total nph/event | Std | Median | Frac. nph > 0 | Mean active channels/event |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        lines.append(
            "| "
            f"{summary.label} | "
            f"{summary.entries} | "
            f"{fmt(summary.mean_total_nph)} | "
            f"{fmt(summary.std_total_nph)} | "
            f"{fmt(summary.median_total_nph)} | "
            f"{fmt(summary.fraction_events_nph_gt_0)} | "
            f"{fmt(summary.mean_active_mppc_channels)} |"
        )
    return "\n".join(lines)


def channel_table(summaries: list[VariantSummary]) -> str:
    lines = [
        "| Canal | TiO2 mean nph | Vikuiti mean nph |",
        "|---|---:|---:|",
    ]
    by_label = {summary.label: summary for summary in summaries}
    for channel in CHANNELS:
        lines.append(
            f"| {channel} | "
            f"{fmt(by_label['TiO2'].channel_means[channel])} | "
            f"{fmt(by_label['Vikuiti'].channel_means[channel])} |"
        )
    return "\n".join(lines)


def write_markdown(
    path: Path,
    summaries: list[VariantSummary],
    ratio: float,
    threads: int,
    commands: list[str],
    build_status: str,
    backends: list[str],
    warnings: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "--short", "HEAD"])
    commit_full = git_value(["rev-parse", "HEAD"])
    roots_ok = all(summary.path.exists() for summary in summaries)
    criteria = [
        ("Build exitoso", build_status),
        ("ROOT TiO2 generado", "ok" if summaries[0].path.exists() else "missing"),
        (
            "ROOT Vikuiti generado",
            "ok" if summaries[1].path.exists() else "missing",
        ),
        ("TTree hodo disponible", "ok" if all(s.tree_name == "hodo" for s in summaries) else "warning"),
        ("Ramas nph_00 ... nph_31", "ok"),
        (
            "Mean total nph/event > 0",
            "ok" if all(s.mean_total_nph > 0 for s in summaries) else "failed",
        ),
        (
            "Mean Vikuiti > TiO2",
            "ok" if summaries[1].mean_total_nph > summaries[0].mean_total_nph else "failed",
        ),
        ("summary_16threads.md generado", "ok"),
    ]
    warning_lines = warnings or ["No additional runtime warnings were captured by this script."]

    text = [
        "# Optical variant comparison, 16 threads",
        "",
        f"- Rama: `{branch}`",
        f"- Commit: `{commit}` (`{commit_full}`)",
        f"- Threads: `{threads}`",
        f"- Backend de analisis: `{', '.join(sorted(set(backends)))}`",
        f"- Build: `{build_status}`",
        f"- ROOT esperados generados: `{'yes' if roots_ok else 'no'}`",
        "",
        "## Comandos ejecutados",
        "",
        "```bash",
        *commands,
        "```",
        "",
        "## Comparacion",
        "",
        markdown_table(summaries),
        "",
        f"- Ratio mean_nph_Vikuiti / mean_nph_TiO2: `{fmt(ratio)}`",
        "",
        "## Channel means",
        "",
        channel_table(summaries),
        "",
        "## Criterios de exito",
        "",
        "| Criterio | Estado |",
        "|---|---|",
        *[f"| {name} | `{status}` |" for name, status in criteria],
        "",
        "## Interpretacion",
        "",
        (
            "nph representa fotones ópticos recolectados idealmente por el volumen "
            "MPPC; todavía no incluye PDE real del S12572-100P, saturación de "
            "pixeles, cross-talk, afterpulsing, ruido oscuro, ganancia electrónica "
            "ni forma de pulso."
        ),
        "",
        "## Warnings y limitaciones",
        "",
        *[f"- {line}" for line in warning_lines],
        "",
    ]
    path.write_text("\n".join(text), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tio2", type=Path, default=DEFAULT_TIO2)
    parser.add_argument("--vikuiti", type=Path, default=DEFAULT_VIKUITI)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--build-status", default="unknown")
    parser.add_argument("--warning", action="append", default=[])
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Command line to include in the Markdown report. May be repeated.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    default_commands = [
        "git switch feat/multithreading",
        "git pull --ff-only",
        "git switch -c test/optical-variant-16threads",
        "rm -rf build",
        "cmake -S . -B build",
        "cmake --build build -j 16",
        "mkdir -p diagnostics/optical_variant_comparison/outputs",
        "HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac",
        "HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac",
        "python3.12 analysis/optical_variant_nph_summary.py --threads 16 --build-status success",
    ]
    commands = args.command or default_commands

    tio2, backend_tio2 = summarize("TiO2", args.tio2)
    vikuiti, backend_vikuiti = summarize("Vikuiti", args.vikuiti)
    ratio = (
        vikuiti.mean_total_nph / tio2.mean_total_nph
        if tio2.mean_total_nph > 0
        else math.inf
    )
    summaries = [tio2, vikuiti]

    write_csv(args.csv, summaries, ratio)
    write_markdown(
        args.markdown,
        summaries,
        ratio,
        args.threads,
        commands,
        args.build_status,
        [backend_tio2, backend_vikuiti],
        args.warning,
    )
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.markdown}")
    print(f"ratio_mean_nph_vikuiti_over_tio2={fmt(ratio)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
