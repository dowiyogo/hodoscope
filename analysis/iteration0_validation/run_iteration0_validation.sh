#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
validation_dir="$repo_root/analysis/iteration0_validation"
build_dir="$repo_root/build"
bin="$build_dir/hodoscope"
script_dir="$validation_dir/scripts"
macro_dir="$validation_dir/macros"
out_dir="$validation_dir/outputs"
root_dir="$out_dir/root"
table_dir="$out_dir/tables"
fig_dir="$out_dir/figures"
log_dir="$out_dir/logs"
summary_md="$validation_dir/ITERATION0_VALIDATION_SUMMARY.md"

mkdir -p "$root_dir" "$table_dir" "$fig_dir" "$log_dir"

if [[ ! -x "$bin" ]]; then
  echo "[validation] Building hodoscope executable"
  cmake --build "$build_dir" -j"${HODO_VALIDATE_JOBS:-$(nproc)}"
fi

mt_threads=${HODO_VALIDATE_MT_THREADS:-$(nproc)}
if [[ "$mt_threads" -gt 8 ]]; then
  mt_threads=8
fi

run_case() {
  local tag="$1"
  local threads="$2"
  local macro="$3"
  local log_file="$log_dir/${tag}.log"

  echo "[validation] Running $tag with HODO_THREADS=$threads"
  (
    cd "$build_dir"
    HODO_THREADS="$threads" "$bin" "$macro" >"$log_file" 2>&1
  )
}

summarize_case() {
  local tag="$1"
  local root_file="$root_dir/${tag}.root"
  python3 "$script_dir/inspect_root_tree.py" "$root_file" \
    --tree hodo \
    --tag "$tag" \
    --out-dir "$out_dir"
  python3 "$script_dir/summarize_edep.py" "$root_file" \
    --tree hodo \
    --tag "$tag" \
    --out-dir "$out_dir"
}

run_case "validate_center_muon_ST" 1 "$macro_dir/validate_center_muon_ST.mac"
run_case "validate_center_muon_MT" "$mt_threads" "$macro_dir/validate_center_muon_MT.mac"
run_case "validate_x_scan_ST" 1 "$macro_dir/validate_x_scan_ST.mac"
run_case "validate_x_scan_MT" "$mt_threads" "$macro_dir/validate_x_scan_MT.mac"
run_case "validate_y_scan_ST" 1 "$macro_dir/validate_y_scan_ST.mac"
run_case "validate_y_scan_MT" "$mt_threads" "$macro_dir/validate_y_scan_MT.mac"

summarize_case "validate_center_muon_ST"
summarize_case "validate_center_muon_MT"
summarize_case "validate_x_scan_ST"
summarize_case "validate_x_scan_MT"
summarize_case "validate_y_scan_ST"
summarize_case "validate_y_scan_MT"

python3 "$script_dir/compare_st_mt.py" \
  --tag center_muon \
  --st-json "$table_dir/validate_center_muon_ST_summary.json" \
  --mt-json "$table_dir/validate_center_muon_MT_summary.json" \
  --st-csv "$table_dir/validate_center_muon_ST_event_summary.csv" \
  --mt-csv "$table_dir/validate_center_muon_MT_event_summary.csv" \
  --out-dir "$out_dir"

python3 "$script_dir/compare_st_mt.py" \
  --tag x_scan \
  --st-json "$table_dir/validate_x_scan_ST_summary.json" \
  --mt-json "$table_dir/validate_x_scan_MT_summary.json" \
  --st-csv "$table_dir/validate_x_scan_ST_event_summary.csv" \
  --mt-csv "$table_dir/validate_x_scan_MT_event_summary.csv" \
  --out-dir "$out_dir"

python3 "$script_dir/compare_st_mt.py" \
  --tag y_scan \
  --st-json "$table_dir/validate_y_scan_ST_summary.json" \
  --mt-json "$table_dir/validate_y_scan_MT_summary.json" \
  --st-csv "$table_dir/validate_y_scan_ST_event_summary.csv" \
  --mt-csv "$table_dir/validate_y_scan_MT_event_summary.csv" \
  --out-dir "$out_dir"

run_date=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git_branch=$(git -C "$repo_root" branch --show-current)
git_commit=$(git -C "$repo_root" rev-parse --short HEAD)
geant4_version="unavailable"
if command -v geant4-config >/dev/null 2>&1; then
  geant4_version=$(geant4-config --version)
fi

python3 "$script_dir/make_iteration0_report.py" \
  --output "$summary_md" \
  --run-date "$run_date" \
  --branch "$git_branch" \
  --commit "$git_commit" \
  --geant4-version "$geant4_version" \
  --tree-json "$table_dir/validate_center_muon_ST_tree.json" \
  --summary-json "$table_dir/validate_center_muon_ST_summary.json" \
  --summary-json "$table_dir/validate_center_muon_MT_summary.json" \
  --summary-json "$table_dir/validate_x_scan_ST_summary.json" \
  --summary-json "$table_dir/validate_x_scan_MT_summary.json" \
  --summary-json "$table_dir/validate_y_scan_ST_summary.json" \
  --summary-json "$table_dir/validate_y_scan_MT_summary.json" \
  --comparison-json "$table_dir/center_muon_st_mt_comparison.json" \
  --comparison-json "$table_dir/x_scan_st_mt_comparison.json" \
  --comparison-json "$table_dir/y_scan_st_mt_comparison.json"

echo "[validation] Summary written to $summary_md"
