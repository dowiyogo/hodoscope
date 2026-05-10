#!/usr/bin/env bash
set -euo pipefail

# Minimal runner for Iteration1 optical validation
ROOT_OUT=outputs/root
TABLES_OUT=outputs/tables
FIG_OUT=outputs/figures
LOG_OUT=outputs/logs

mkdir -p "$ROOT_OUT" "$TABLES_OUT" "$FIG_OUT" "$LOG_OUT"

echo "Iteration1 optical validation run: $(date)" | tee "$LOG_OUT/run_info.log"
echo "Git branch: $(git rev-parse --abbrev-ref HEAD)" | tee -a "$LOG_OUT/run_info.log"
echo "Commit: $(git rev-parse --short HEAD)" | tee -a "$LOG_OUT/run_info.log"
echo "HODO_ENABLE_OPTICAL=${HODO_ENABLE_OPTICAL:-0}" | tee -a "$LOG_OUT/run_info.log"
echo "HODO_THREADS=${HODO_THREADS:-unset}" | tee -a "$LOG_OUT/run_info.log"

# Locations
BIN=./hodoscope

run_macro() {
  local macro=$1
  local logfile=$2
  echo "Running $macro -> $logfile"
  (exec $BIN "$macro") > "$logfile" 2>&1 || true
}

# Control (optical OFF)
export HODO_ENABLE_OPTICAL=${HODO_ENABLE_OPTICAL:-0}
run_macro macros/optical_off_center_muon.mac "$LOG_OUT/optical_off_center_muon.log"

if [ "${HODO_ENABLE_OPTICAL}" = "1" ]; then
  run_macro macros/optical_on_center_muon.mac  "$LOG_OUT/optical_on_center_muon.log"
  run_macro macros/optical_on_x_scan.mac      "$LOG_OUT/optical_on_x_scan.log"
  run_macro macros/optical_on_y_scan.mac      "$LOG_OUT/optical_on_y_scan.log"
  run_macro macros/optical_debug_few_events.mac "$LOG_OUT/optical_debug_few_events.log"
fi

# Run analysis scripts (python, using uproot)
python3 scripts/inspect_optical_root.py outputs/root > "$LOG_OUT/inspect_root.log" || true
python3 scripts/summarize_optical_response.py outputs/root > "$TABLES_OUT/summary_optical.csv" || true
python3 scripts/compare_optical_off_on.py outputs/root > "$TABLES_OUT/compare_off_on.md" || true
python3 scripts/make_iteration1_optical_report.py outputs > ITERATION1_OPTICAL_VALIDATION_SUMMARY.md || true

echo "Iteration1 validation completed. See outputs/" | tee -a "$LOG_OUT/run_info.log"
