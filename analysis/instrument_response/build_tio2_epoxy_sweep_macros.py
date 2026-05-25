#!/usr/bin/env python3.12
"""Generate central-gun macros for TiO2+epoxy reflector sensitivity sweeps."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_OUTDIR = Path("diagnostics/instrument_response/tio2_epoxy_sweep/macros")
OUTPUT_DIR = Path("diagnostics/instrument_response/tio2_epoxy_sweep/outputs")


def parse_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def tag_float(value: float) -> str:
    return f"{value:.3f}".replace(".", "p")


def macro(
    name: str,
    variant: str,
    events: int,
    r425: float | None = None,
    surface_mode: str | None = None,
) -> str:
    lines = [
        f"# TiO2+epoxy reflector sweep macro: {name}",
        "/control/verbose 1",
        "/run/verbose 1",
        "/event/verbose 0",
        "/tracking/verbose 0",
        f"/analysis/setFileName {OUTPUT_DIR / (name + '.root')}",
        f"/hodoscope/setDetectorVariant {variant}",
        "/hodoscope/det/optical true",
        "/hodoscope/det/improvedOptical true",
        "/hodoscope/det/setD 5.0 mm",
    ]
    if r425 is not None:
        lines.append(f"/hodoscope/det/tio2EpoxyEffectiveR425 {r425:.6g}")
    if surface_mode is not None:
        lines.append(f"/hodoscope/det/tio2EpoxySurfaceMode {surface_mode}")
    lines.extend(
        [
            "/run/initialize",
            "/gun/particle mu-",
            "/gun/energy 4.0 GeV",
            "/gun/position 0.0 0.0 50.0 mm",
            "/gun/direction 0.0 0.0 -1.0",
            f"/run/beamOn {events}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=int, default=500)
    parser.add_argument("--r425-list", default="0.93,0.95,0.97,0.98,0.985,0.99")
    parser.add_argument("--surface-modes", default="diffuse")
    parser.add_argument("--include-baseline", default="true")
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    include_baseline = parse_bool(str(args.include_baseline))
    r425_values = [float(item) for item in args.r425_list.split(",") if item.strip()]
    modes = [item.strip().lower() for item in args.surface_modes.split(",") if item.strip()]

    generated: list[Path] = []
    if include_baseline:
        path = args.outdir / "sweep_tio2_baseline.mac"
        path.write_text(macro("sweep_tio2_baseline", "Hod2019", args.events), encoding="utf-8")
        generated.append(path)
        path = args.outdir / "sweep_vikuiti_baseline.mac"
        path.write_text(macro("sweep_vikuiti_baseline", "Hod2018", args.events), encoding="utf-8")
        generated.append(path)

    for mode in modes:
        if mode not in {"default", "diffuse", "specular"}:
            raise ValueError(f"Invalid surface mode: {mode}")
        for r425 in r425_values:
            name = f"sweep_tio2_epoxy_R425_{tag_float(r425)}_{mode}"
            path = args.outdir / f"{name}.mac"
            path.write_text(
                macro(name, "Hod2019", args.events, r425=r425, surface_mode=mode),
                encoding="utf-8",
            )
            generated.append(path)

    for path in generated:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
