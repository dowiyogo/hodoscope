#!/usr/bin/env python3.12
"""Build intermediate TiO2+epoxy XY position-scan macros."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_OUTDIR = Path("diagnostics/instrument_response/tio2_epoxy_position_scan/macros")
OUTPUT_DIR = Path("diagnostics/instrument_response/tio2_epoxy_position_scan/outputs")


def frange(start: float, stop: float, step: float) -> list[float]:
    values: list[float] = []
    value = start
    eps = abs(step) * 1.0e-9
    while value <= stop + eps:
        values.append(round(value, 10))
        value += step
    return values


def tag_float(value: float) -> str:
    return f"{value:.3f}".replace(".", "p")


def macro_text(
    r425: float,
    xs: list[float],
    ys: list[float],
    events_per_point: int,
    name_suffix: str,
) -> str:
    tag = tag_float(r425)
    suffix = f"_{name_suffix}" if name_suffix else ""
    name = f"position_scan_tio2_epoxy_R425_{tag}_diffuse{suffix}"
    scan_label = "Production" if name_suffix == "production" else "Intermediate"
    lines = [
        f"# {scan_label} TiO2+epoxy position scan, R425={r425:.3f}, diffuse",
        "/control/verbose 1",
        "/run/verbose 1",
        "/event/verbose 0",
        "/tracking/verbose 0",
        f"/analysis/setFileName {OUTPUT_DIR / (name + '.root')}",
        "/hodoscope/setDetectorVariant Hod2019",
        "/hodoscope/det/optical true",
        "/hodoscope/det/improvedOptical true",
        "/hodoscope/det/setD 5.0 mm",
        f"/hodoscope/det/tio2EpoxyEffectiveR425 {r425:.6g}",
        "/hodoscope/det/tio2EpoxySurfaceMode diffuse",
        "/run/initialize",
        "/gun/particle mu-",
        "/gun/energy 4.0 GeV",
        "/gun/direction 0.0 0.0 -1.0",
        "",
    ]
    for y in ys:
        for x in xs:
            lines.append(f"/gun/position {x:.6g} {y:.6g} 50.0 mm")
            lines.append(f"/run/beamOn {events_per_point}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r425-list", default="0.954,0.956")
    parser.add_argument("--events-per-point", type=int, default=20)
    parser.add_argument("--xmin", type=float, default=-16.0)
    parser.add_argument("--xmax", type=float, default=16.0)
    parser.add_argument("--dx", type=float, default=2.0)
    parser.add_argument("--ymin", type=float, default=-16.0)
    parser.add_argument("--ymax", type=float, default=16.0)
    parser.add_argument("--dy", type=float, default=2.0)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument(
        "--name-suffix",
        default="",
        help="Optional suffix for macro and ROOT names, e.g. production.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    xs = frange(args.xmin, args.xmax, args.dx)
    ys = frange(args.ymin, args.ymax, args.dy)
    r425_values = [float(item) for item in args.r425_list.split(",") if item.strip()]

    for r425 in r425_values:
        tag = tag_float(r425)
        suffix = f"_{args.name_suffix}" if args.name_suffix else ""
        path = args.outdir / f"position_scan_tio2_epoxy_R425_{tag}_diffuse{suffix}.mac"
        path.write_text(
            macro_text(r425, xs, ys, args.events_per_point, args.name_suffix),
            encoding="utf-8",
        )
        print(
            f"Wrote {path} with {len(xs)} x {len(ys)} points, "
            f"{args.events_per_point} events/point"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
