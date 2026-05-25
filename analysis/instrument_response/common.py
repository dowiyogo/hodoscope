#!/usr/bin/env python3.12
"""Shared helpers for hodoscope instrument-response studies."""

from __future__ import annotations

import csv
import importlib
import math
import subprocess
import sys
from pathlib import Path
from typing import Iterable


CHANNELS = [f"{i:02d}" for i in range(32)]
EDEP_BRANCHES = [f"edep_{i:02d}" for i in range(32)]
NPH_BRANCHES = [f"nph_{i:02d}" for i in range(32)]
PRIMARY_BRANCHES = ["prim_x", "prim_y", "prim_z", "prim_px", "prim_py", "prim_pz"]

OUTDIR = Path("diagnostics/instrument_response")
TABLE_DIR = OUTDIR / "tables"
FIGURE_DIR = OUTDIR / "figures"

VARIANT_ROOTS = {
    "tio2": OUTDIR / "outputs" / "position_scan_tio2.root",
    "vikuiti": OUTDIR / "outputs" / "position_scan_vikuiti.root",
}

VARIANT_LABELS = {
    "tio2": "Hod2019/TiO2",
    "vikuiti": "Hod2018/Vikuiti",
}


def ensure_dirs() -> None:
    for path in [OUTDIR, TABLE_DIR, FIGURE_DIR, OUTDIR / "outputs", OUTDIR / "logs"]:
        path.mkdir(parents=True, exist_ok=True)


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True)


def import_or_install(package: str, install_packages: list[str]) -> object:
    try:
        return importlib.import_module(package)
    except ImportError as first_error:
        cmd = ["python3.12", "-m", "pip", "install", "--user", *install_packages]
        print(
            f"{package} is not importable; trying: {' '.join(cmd)}",
            file=sys.stderr,
        )
        proc = run_checked(cmd)
        if proc.returncode != 0:
            raise RuntimeError(
                f"Could not import {package} ({first_error}) and automatic "
                f"install failed with exit code {proc.returncode}.\n"
                f"Install dependencies with:\n  {' '.join(cmd)}"
            ) from first_error
        importlib.invalidate_caches()
        try:
            return importlib.import_module(package)
        except Exception as second_error:
            raise RuntimeError(
                f"Could not import {package} after automatic install: {second_error}\n"
                f"Install dependencies with:\n  {' '.join(cmd)}"
            ) from second_error


def get_uproot() -> object:
    return import_or_install(
        "uproot", ["uproot", "awkward", "numpy", "pandas", "matplotlib"]
    )


def get_numpy() -> object:
    return import_or_install("numpy", ["numpy"])


def get_pandas() -> object:
    return import_or_install("pandas", ["pandas"])


def get_matplotlib_pyplot() -> object:
    import_or_install("matplotlib", ["matplotlib"])
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def read_hodo_arrays(root_path: Path, branches: list[str] | None = None) -> dict[str, object]:
    uproot = get_uproot()
    if not root_path.exists():
        raise FileNotFoundError(root_path)
    requested = branches or [*PRIMARY_BRANCHES, *EDEP_BRANCHES, *NPH_BRANCHES]
    with uproot.open(root_path) as root_file:
        if "hodo" not in root_file:
            raise RuntimeError(f"{root_path} does not contain TTree 'hodo'")
        tree = root_file["hodo"]
        missing = [name for name in requested if name not in tree.keys()]
        if missing:
            raise RuntimeError(f"{root_path} is missing branches: {', '.join(missing)}")
        arrays = tree.arrays(requested, library="np")
    return {name: arrays[name] for name in requested}


def channel_centers() -> dict[str, list[float]]:
    upper = [-14.0 + 4.0 * i for i in range(8)]
    lower = [value + 2.0 for value in upper]
    return {
        "x": [*upper, *lower],
        "y": [*upper, *lower],
    }


def weighted_reco(values: object, centers: list[float], threshold: float):
    np = get_numpy()
    weights = np.asarray(values, dtype=float)
    active = weights > threshold
    denom = weights.sum(axis=1)
    center_arr = np.asarray(centers, dtype=float)
    reco = np.full(weights.shape[0], np.nan)
    ok = denom > 0
    reco[ok] = (weights[ok] * center_arr).sum(axis=1) / denom[ok]
    n_active = active.sum(axis=1)
    return reco, n_active


def robust_stats(values: object) -> dict[str, float]:
    np = get_numpy()
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"entries": 0, "bias": math.nan, "sigma": math.nan, "rms_robust": math.nan}
    median = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median)))
    return {
        "entries": int(arr.size),
        "bias": float(np.mean(arr)),
        "sigma": float(np.std(arr)),
        "rms_robust": 1.4826 * mad,
    }


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def fmt(value: float) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and math.isnan(value):
        return "nan"
    return f"{float(value):.6g}"


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(
            ["git", *args], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return default
