#!/usr/bin/env bash
set -euo pipefail

# Minimal runner for Iteration1 optical validation
ROOT_OUT=outputs/root
TABLES_OUT=outputs/tables
FIG_OUT=outputs/figures
LOG_OUT=outputs/logs

cd "$(dirname "$0")/../.."
repo_root=$(pwd)
validation_dir="$repo_root/analysis/iteration1_optical_validation"
build_dir="$repo_root/build"
bin="$build_dir/hodoscope"
script_dir="$validation_dir/scripts"
macro_dir="$validation_dir/macros"
out_dir="$validation_dir/outputs"
root_dir="$out_dir/root"
table_dir="$out_dir/tables"
fig_dir="$out_dir/figures"
log_dir="$out_dir/logs"
summary_md="$validation_dir/ITERATION1_OPTICAL_VALIDATION_SUMMARY.md"

mkdir -p "$root_dir" "$table_dir" "$fig_dir" "$log_dir"

echo "Iteration1 optical validation run: $(date)" | tee "$log_dir/run_info.log"
echo "Git branch: $(git -C "$repo_root" rev-parse --abbrev-ref HEAD)" | tee -a "$log_dir/run_info.log"
echo "Commit: $(git -C "$repo_root" rev-parse --short HEAD)" | tee -a "$log_dir/run_info.log"
echo "HODO_ENABLE_OPTICAL=${HODO_ENABLE_OPTICAL:-0}" | tee -a "$log_dir/run_info.log"
echo "HODO_THREADS=${HODO_THREADS:-unset}" | tee -a "$log_dir/run_info.log"

if [[ ! -x "$bin" ]]; then
  echo "[validation] Building hodoscope executable" | tee -a "$log_dir/run_info.log"
  cmake --build "$build_dir" -j"${HODO_VALIDATE_JOBS:-$(nproc)}" | tee -a "$log_dir/run_info.log"
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

  echo "[validation] Running $tag with HODO_THREADS=$threads" | tee -a "$log_dir/run_info.log"
  (
    cd "$validation_dir"
    HODO_THREADS="$threads" HODO_ENABLE_OPTICAL="${HODO_ENABLE_OPTICAL:-0}" "$bin" "$macro" >"$log_file" 2>&1 || true
  )
}

run_case "optical_off_center_muon" 1 "$macro_dir/optical_off_center_muon.mac"
if [[ "${HODO_ENABLE_OPTICAL:-0}" == "1" ]]; then
  # Run optical cases in single-thread to avoid MT issues during iteration1
  run_case "optical_on_center_muon" 1 "$macro_dir/optical_on_center_muon.mac"
  run_case "optical_on_x_scan" 1 "$macro_dir/optical_on_x_scan.mac"
  run_case "optical_on_y_scan" 1 "$macro_dir/optical_on_y_scan.mac"
  run_case "optical_debug_few_events" 1 "$macro_dir/optical_debug_few_events.mac"
fi

# Summarize
python3 "$script_dir/inspect_optical_root.py" "$root_dir" > "$log_dir/inspect_root.log" || true
python3 "$script_dir/summarize_optical_response.py" "$root_dir" > "$table_dir/summary_optical.csv" || true
python3 "$script_dir/compare_optical_off_on.py" "$root_dir" > "$table_dir/compare_off_on.md" || true
python3 "$script_dir/make_iteration1_optical_report.py" "$out_dir" > "$summary_md" || true

echo "Iteration1 validation completed. See $out_dir" | tee -a "$log_dir/run_info.log"
