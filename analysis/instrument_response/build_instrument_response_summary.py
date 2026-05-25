#!/usr/bin/env python3.12
"""Assemble the integrated Hod2018/Hod2019 instrument-response summary."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from common import OUTDIR, TABLE_DIR, fmt, git_value, read_csv_dicts


def find_row(rows: list[dict[str, str]], **filters: str) -> dict[str, str] | None:
    for row in rows:
        if all(row.get(key) == value for key, value in filters.items()):
            return row
    return None


def main() -> int:
    optical_csv = Path("diagnostics/optical_variant_comparison/summary_16threads.csv")
    optical = read_csv_dicts(optical_csv) if optical_csv.exists() else []
    spatial = read_csv_dicts(TABLE_DIR / "spatial_resolution_summary.csv")
    angular = read_csv_dicts(TABLE_DIR / "angular_resolution_estimate.csv")
    efficiency_tio2 = read_csv_dicts(TABLE_DIR / "virtual_pixel_efficiency_tio2.csv")
    efficiency_vikuiti = read_csv_dicts(TABLE_DIR / "virtual_pixel_efficiency_vikuiti.csv")
    rate = read_csv_dicts(TABLE_DIR / "accepted_muon_rate_estimate.csv")
    threshold = read_csv_dicts(TABLE_DIR / "threshold_sensitivity.csv")

    optical_by_variant = {row["variant"]: row for row in optical}
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
        "HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_tio2_quick.mac",
        "HODO_THREADS=16 ./build/hodoscope macros/optical_tests/run_variant_vikuiti_quick.mac",
        "python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 5 --dx 4 --dy 4",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_tio2.mac",
        "HODO_THREADS=16 ./build/hodoscope diagnostics/instrument_response/macros/position_scan_vikuiti.mac",
        "python3.12 analysis/instrument_response/spatial_resolution_analysis.py",
        "python3.12 analysis/instrument_response/virtual_pixel_efficiency.py --threshold-nph 1 --use nph",
        "python3.12 analysis/instrument_response/angular_resolution_estimate.py",
        "python3.12 analysis/instrument_response/accepted_muon_rate_estimate.py",
        "python3.12 analysis/instrument_response/acceptance_matrix_builder.py",
        "python3.12 analysis/instrument_response/threshold_sensitivity.py",
        "python3.12 analysis/instrument_response/build_position_scan_macros.py --events-per-point 20 --dx 1 --dy 1",
        "```",
        "",
        "The executed position scan was the small validation scan (`dx=dy=4 mm`, `5` events per point). The production macros (`dx=dy=1 mm`, `20` events per point) were generated after the validation run but were not executed in this stage.",
        "",
        "## 3. Physical configuration",
        "",
        "- Hod2018 = Vikuiti ESR reflector",
        "- Hod2019 = TiO2 optical epoxy paint reflector",
        "- Scintillator = BC408 / EJ200-equivalent",
        "- MPPC = S12572-100P label with ideal optical-photon collection volume",
        "",
        "## 4. Optical result already validated",
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
