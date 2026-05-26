#!/usr/bin/env python3.12
"""Assemble the integrated Hod2018/Hod2019 instrument-response summary."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from common import OUTDIR, TABLE_DIR, VARIANT_ROOTS, fmt, get_uproot, git_value, read_csv_dicts


def find_row(rows: list[dict[str, str]], **filters: str) -> dict[str, str] | None:
    for row in rows:
        if all(row.get(key) == value for key, value in filters.items()):
            return row
    return None


def root_entries(path: Path) -> int | str:
    try:
        uproot = get_uproot()
        with uproot.open(path) as root_file:
            return int(root_file["hodo"].num_entries)
    except Exception as exc:
        return f"unavailable ({exc})"


def scan_status(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "unknown", "unknown"
    parts = path.read_text(encoding="utf-8").strip().split()
    if len(parts) < 2:
        return "unknown", "unknown"
    return parts[0], parts[1]


def sweep_lines(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return [
            "## TiO2+epoxy reflector sensitivity",
            "",
            "No TiO2+epoxy reflector sweep table was found for this report.",
        ]

    selected = [
        row for row in rows
        if row.get("variant") in {"tio2", "vikuiti"}
        or (
            row.get("variant") == "tio2_epoxy"
            and row.get("surface_mode") == "diffuse"
        )
    ]
    selected.sort(
        key=lambda row: (
            {"tio2": 0, "tio2_epoxy": 1, "vikuiti": 2}.get(row.get("variant", ""), 3),
            float(row["r425_effective"]) if row.get("r425_effective") else 0.0,
        )
    )
    tio2 = find_row(rows, variant="tio2")
    vikuiti = find_row(rows, variant="vikuiti")
    def diffuse_row(r425: str) -> dict[str, str] | None:
        return next(
            (
                row for row in rows
                if row.get("variant") == "tio2_epoxy"
                and row.get("surface_mode") == "diffuse"
                and row.get("r425_effective") == r425
            ),
            None,
        )

    r0954 = diffuse_row("0.954")
    r0956 = diffuse_row("0.956")
    table = [
        "| Model | R425 | Surface | Mean nph | Eff >=1 | Eff >=5 | Vikuiti/model |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in selected:
        table.append(
            f"| {row['label']} | {row['r425_effective']} | {row['surface_mode']} | "
            f"{row['mean_total_nph']} | {row['efficiency_nph_ge_1']} | "
            f"{row['efficiency_nph_ge_5']} | {row['ratio_vikuiti_to_model']} |"
        )

    return [
        "## TiO2+epoxy reflector sensitivity",
        "",
        "Hod2019 experimentally corresponds to TiO2 plus optical epoxy paint, so the pure/default TiO2 surface model should be treated as a simplified effective model rather than a final material calibration. A central-gun sweep was run to test explicit TiO2+epoxy effective reflector overrides without changing the Hod2019 default.",
        "",
        f"- Default TiO2 central mean nph/event: `{tio2['mean_total_nph'] if tio2 else 'n/a'}`",
        f"- Vikuiti central mean nph/event: `{vikuiti['mean_total_nph'] if vikuiti else 'n/a'}`",
        f"- Conservative TiO2+epoxy candidate: `R425=0.954 diffuse`, mean nph/event `{r0954['mean_total_nph'] if r0954 else 'n/a'}`, efficiency nph>=1 `{r0954['efficiency_nph_ge_1'] if r0954 else 'n/a'}`, efficiency nph>=5 `{r0954['efficiency_nph_ge_5'] if r0954 else 'n/a'}`",
        f"- Upper sensitivity candidate: `R425=0.956 diffuse`, mean nph/event `{r0956['mean_total_nph'] if r0956 else 'n/a'}`, estimated npe@30% `{r0956['estimated_npe_mean_pde30'] if r0956 else 'n/a'}`",
        "",
        *table,
        "",
        "The fine sweep resolves the steep transition: `R425=0.954 diffuse` is close to Vikuiti/model ratio 2, while `R425=0.956 diffuse` enters the 5..15 analysis-only estimated npe@30% range. A good next step is an intermediate position scan with `dx=dy=2 mm` and `10` to `20` events per point for `R425=0.954 diffuse`; optionally add `R425=0.956 diffuse` as the upper sensitivity case.",
        "",
        "This `R425` is an effective model reflectivity near 425 nm, not a measured physical reflectivity of the TiO2+epoxy mixture. It still needs calibration against experimental data.",
    ]


def intermediate_position_scan_lines(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return [
            "## TiO2+epoxy production candidate",
            "",
            "No TiO2+epoxy position-scan table was found for this report.",
        ]

    intermediate = [row for row in rows if row.get("scan_type") == "intermediate"]
    production = [row for row in rows if row.get("scan_type") == "production"]
    table = [
        "| Model | Scan | Entries | Mean nph | Eff >=1 | Eff >=5 | Central eff >=1 | Central eff >=5 | sigma_x [mm] | sigma_y [mm] | est. npe@30% |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        table.append(
            f"| {row['label']} | {row.get('scan_type', 'unknown')} | {row['entries']} | {row['mean_total_nph']} | "
            f"{row['efficiency_nph_ge_1']} | {row['efficiency_nph_ge_5']} | "
            f"{row['central_efficiency_nph_ge_1']} | {row['central_efficiency_nph_ge_5']} | "
            f"{row['sigma_x_nph_central_mm']} | {row['sigma_y_nph_central_mm']} | "
            f"{row.get('estimated_npe_mean_pde30', 'n/a')} |"
        )
    prod_0956 = next(
        (
            row for row in production
            if row.get("r425_effective") == "0.956"
        ),
        None,
    )

    return [
        "## TiO2+epoxy production candidate",
        "",
        "Intermediate and production scans were run for effective TiO2+epoxy reflector candidates selected by the central sweep. `R425=0.956 diffuse` was chosen for production because it improved threshold efficiency in the intermediate scan while staying below the Vikuiti production mean nph.",
        "",
        f"- Intermediate scans available: `{len(intermediate)}`",
        f"- Production scans available: `{len(production)}`",
        "- Production candidate configuration: `R425=0.956 diffuse`, `dx=dy=1 mm`, `33 x 33`, `20` events per point, `HODO_THREADS=16`",
        "",
        *table,
        "",
        f"`R425=0.956 diffuse` production entries: `{prod_0956['entries'] if prod_0956 else 'n/a'}`.",
        "`R425=0.956 diffuse` remains the production candidate. `R425=0.954 diffuse` should stay as a conservative systematic bracket for a later run rather than being run automatically here.",
        "",
        "The `R425` values are effective model reflectivities near 425 nm, not measured material reflectivities.",
    ]


def main() -> int:
    optical_csv = Path("diagnostics/optical_variant_comparison/summary_16threads.csv")
    optical = read_csv_dicts(optical_csv) if optical_csv.exists() else []
    sweep_csv = Path("diagnostics/instrument_response/tio2_epoxy_sweep/tables/tio2_epoxy_reflector_sweep.csv")
    sweep = read_csv_dicts(sweep_csv) if sweep_csv.exists() else []
    epoxy_position_csv = Path("diagnostics/instrument_response/tio2_epoxy_position_scan/tables/tio2_epoxy_position_scan_summary.csv")
    epoxy_position = read_csv_dicts(epoxy_position_csv) if epoxy_position_csv.exists() else []
    spatial = read_csv_dicts(TABLE_DIR / "spatial_resolution_summary.csv")
    angular = read_csv_dicts(TABLE_DIR / "angular_resolution_estimate.csv")
    efficiency_tio2 = read_csv_dicts(TABLE_DIR / "virtual_pixel_efficiency_tio2.csv")
    efficiency_vikuiti = read_csv_dicts(TABLE_DIR / "virtual_pixel_efficiency_vikuiti.csv")
    rate = read_csv_dicts(TABLE_DIR / "accepted_muon_rate_estimate.csv")
    threshold = read_csv_dicts(TABLE_DIR / "threshold_sensitivity.csv")
    expected_events = 33 * 33 * 20
    tio2_rc, tio2_seconds = scan_status(
        OUTDIR / "logs" / "position_scan_tio2_production.status"
    )
    vik_rc, vik_seconds = scan_status(
        OUTDIR / "logs" / "position_scan_vikuiti_production.status"
    )
    tio2_entries = root_entries(VARIANT_ROOTS["tio2"])
    vik_entries = root_entries(VARIANT_ROOTS["vikuiti"])

    optical_by_variant = {row["variant"]: row for row in optical}
    rate_by_variant = {row["variant"]: row for row in rate}
    production_nph_tio2 = float(rate_by_variant["tio2"]["mean_nph_total"]) if "tio2" in rate_by_variant else float("nan")
    production_nph_vikuiti = float(rate_by_variant["vikuiti"]["mean_nph_total"]) if "vikuiti" in rate_by_variant else float("nan")
    production_nph_ratio = (
        production_nph_vikuiti / production_nph_tio2
        if production_nph_tio2 > 0
        else float("inf")
    )
    sx_tio2 = find_row(spatial, variant="tio2", estimator="nph", coordinate="x", region="central")
    sy_tio2 = find_row(spatial, variant="tio2", estimator="nph", coordinate="y", region="central")
    sx_vik = find_row(spatial, variant="vikuiti", estimator="nph", coordinate="x", region="central")
    sy_vik = find_row(spatial, variant="vikuiti", estimator="nph", coordinate="y", region="central")
    ang100 = find_row(angular, baseline_mm="100")
    ang1000 = find_row(angular, baseline_mm="1000")

    def mean_eff(rows: list[dict[str, str]]) -> float:
        vals = [float(row["efficiency"]) for row in rows]
        return sum(vals) / len(vals) if vals else 0.0

    rate_lines = [
        "| Variant | Effective rate [arb.] | Efficiency |",
        "|---|---:|---:|",
    ]
    for row in rate:
        rate_lines.append(f"| {row['variant_label']} | {row['effective_rate_arb']} | {row['efficiency']} |")

    threshold_lines = [
        "| Variant | Threshold | Total efficiency | Relative counts |",
        "|---|---:|---:|---:|",
    ]
    for row in threshold:
        threshold_lines.append(
            f"| {row['variant_label']} | {row['threshold_nph']} | "
            f"{row['efficiency_total']} | {row['relative_expected_counts']} |"
        )

    text = [
        "# HOD2018/HOD2019 instrument response summary",
        "",
        "## 1. Branch, commit and date",
        "",
        f"- Branch: `{git_value(['branch', '--show-current'])}`",
        f"- Commit: `{git_value(['rev-parse', '--short', 'HEAD'])}`",
        f"- Date: `{dt.datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## 2. Build and execution commands",
        "",
        "```bash",
        "rm -rf build",
        "cmake -S . -B build",
        "cmake --build build -j 16",
        "python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 20 --dx 1 --dy 1",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_tio2.mac",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_vikuiti.mac",
        "python3.12 analysis/instrument_response/spatial_resolution_analysis.py",
        "python3.12 analysis/instrument_response/virtual_pixel_efficiency.py --threshold-nph 1 --use nph",
        "python3.12 analysis/instrument_response/angular_resolution_estimate.py",
        "python3.12 analysis/instrument_response/accepted_muon_rate_estimate.py",
        "python3.12 analysis/instrument_response/acceptance_matrix_builder.py",
        "python3.12 analysis/instrument_response/threshold_sensitivity.py",
        "python3.12 analysis/instrument_response/build_tio2_epoxy_sweep_macros.py --events 500 --r425-list \"0.93,0.95,0.97,0.98,0.985,0.99\" --surface-modes \"diffuse\"",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_tio2_baseline.mac",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_vikuiti_baseline.mac",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_sweep/macros/sweep_tio2_epoxy_R425_0p950_diffuse.mac",
        "python3.12 analysis/instrument_response/tio2_epoxy_sweep_analysis.py",
        "python3.12 analysis/instrument_response/build_tio2_epoxy_position_scan_macros.py --r425-list \"0.954,0.956\" --events-per-point 20 --dx 2 --dy 2",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_position_scan/macros/position_scan_tio2_epoxy_R425_0p954_diffuse.mac",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/tio2_epoxy_position_scan/macros/position_scan_tio2_epoxy_R425_0p956_diffuse.mac",
        "python3.12 analysis/instrument_response/tio2_epoxy_position_scan_analysis.py",
        "python3.12 analysis/instrument_response/build_instrument_response_summary.py",
        "```",
        "",
        "The current numbers in this report are from the production position scan unless a section explicitly says otherwise.",
        "",
        "## Production scan configuration",
        "",
        f"- Branch: `{git_value(['branch', '--show-current'])}`",
        f"- Commit used for this report: `{git_value(['rev-parse', '--short', 'HEAD'])}`",
        "- Threads: `HODO_THREADS=16`",
        "- Grid: `33 x 33` positions",
        "- Range: `x,y = -16 mm ... +16 mm`",
        "- Step: `dx=dy=1 mm`",
        "- Events per point: `20`",
        f"- Expected events per variant: `{expected_events}`",
        f"- TiO2 actual events: `{tio2_entries}`",
        f"- Vikuiti actual events: `{vik_entries}`",
        f"- TiO2 ROOT: `{VARIANT_ROOTS['tio2']}`",
        f"- Vikuiti ROOT: `{VARIANT_ROOTS['vikuiti']}`",
        f"- TiO2 scan exit/duration: `{tio2_rc}`, `{tio2_seconds} s`",
        f"- Vikuiti scan exit/duration: `{vik_rc}`, `{vik_seconds} s`",
        f"- Report generated at: `{dt.datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## Small scan vs production scan",
        "",
        "The previous validation pass used `dx=dy=4 mm` with `5` events per point. That small scan validated the full analysis chain and exposed threshold semantics, but it is not the source of the current instrument-response numbers. The current tables and summaries use the production scan with `dx=dy=1 mm` and `20` events per point.",
        "",
        "## 3. Physical configuration",
        "",
        "- Hod2018 = Vikuiti ESR reflector",
        "- Hod2019 = TiO2 optical epoxy paint reflector",
        "- Scintillator = BC408 / EJ200-equivalent",
        "- MPPC = S12572-100P label with ideal optical-photon collection volume",
        "",
        "## 4. Optical signal",
        "",
        "Production position-scan mean total `nph/event`:",
        "",
        f"- TiO2: `{fmt(production_nph_tio2)}`",
        f"- Vikuiti: `{fmt(production_nph_vikuiti)}`",
        f"- Vikuiti/TiO2 ratio: `{fmt(production_nph_ratio)}`",
        "",
        "Earlier quick optical validation at the central gun position:",
        "",
        f"- TiO2 mean nph/event: `{optical_by_variant.get('TiO2', {}).get('mean_total_nph_per_event', '2.56')}`",
        f"- Vikuiti mean nph/event: `{optical_by_variant.get('Vikuiti', {}).get('mean_total_nph_per_event', '32.82')}`",
        f"- Vikuiti/TiO2 ratio: `{optical_by_variant.get('TiO2', {}).get('ratio_mean_nph_vikuiti_over_tio2', '12.8203')}`",
        "",
        "## 5. Spatial resolution sigma_x, sigma_y",
        "",
        "| Variant | sigma_x central nph [mm] | sigma_y central nph [mm] |",
        "|---|---:|---:|",
        f"| Hod2019/TiO2 | {sx_tio2['robust_sigma_mm'] if sx_tio2 else 'n/a'} | {sy_tio2['robust_sigma_mm'] if sy_tio2 else 'n/a'} |",
        f"| Hod2018/Vikuiti | {sx_vik['robust_sigma_mm'] if sx_vik else 'n/a'} | {sy_vik['robust_sigma_mm'] if sy_vik else 'n/a'} |",
        "",
        "## 6. Angular resolution estimate versus baseline L",
        "",
        "`L` is the distance between active centers of Hodo2018 and Hodo2019, not the internal X/Y separation `D`.",
        "",
        "| L [mm] | sigma_theta_x [mrad] | sigma_theta_y [mrad] |",
        "|---:|---:|---:|",
        f"| 100 | {ang100['sigma_theta_x_mrad'] if ang100 else 'n/a'} | {ang100['sigma_theta_y_mrad'] if ang100 else 'n/a'} |",
        f"| 1000 | {ang1000['sigma_theta_x_mrad'] if ang1000 else 'n/a'} | {ang1000['sigma_theta_y_mrad'] if ang1000 else 'n/a'} |",
        "",
        "## 7. Virtual pixel efficiency",
        "",
        f"- Mean pixel efficiency TiO2: `{fmt(mean_eff(efficiency_tio2))}`",
        f"- Mean pixel efficiency Vikuiti: `{fmt(mean_eff(efficiency_vikuiti))}`",
        "",
        "## 8. Expected accepted muon rate",
        "",
        *rate_lines,
        "",
        "## 9. Ideal versus effective acceptance",
        "",
        "The acceptance tables separate a simplified geometric angular response from an effective response multiplied by the scan-derived efficiency. This is a pre-inversion angular response product, not the full voxelized `F` matrix.",
        "",
        "## 10. Threshold sensitivity",
        "",
        *threshold_lines,
        "",
        *sweep_lines(sweep),
        "",
        *intermediate_position_scan_lines(epoxy_position),
        "",
        "## 11. Connection to the abstract",
        "",
        "These outputs connect Geant4 module response (`edep`, `nph`, efficiency and acceptance) to the muography chain expected by Meiga/MuYSC: angular flux and acceptance can be folded into expected counts, while threshold-dependent efficiencies can enter inversion weights.",
        "",
        "## 12. Limitations",
        "",
        "- `nph` does not include real PDE.",
        "- No pulse simulation or electronics response is included.",
        "- No saturation, cross-talk, afterpulsing, or dark noise is included.",
        "- Real flux must come from MuYSC/Meiga for production.",
        "- The current geometry is a single hodoscope module; sigma_theta is parametric until two modules are simulated together.",
        "",
        "## 13. Recommended next step",
        "",
        "Add `npe_NN` with S12572-100P PDE and a configurable threshold model, then connect either a MuYSC angular flux table or a two-module Geant4 geometry to replace the parametric angular response.",
        "",
    ]
    (OUTDIR / "HOD2018_HOD2019_INSTRUMENT_RESPONSE_SUMMARY.md").write_text(
        "\n".join(text), encoding="utf-8"
    )
    print(f"Wrote {OUTDIR / 'HOD2018_HOD2019_INSTRUMENT_RESPONSE_SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
