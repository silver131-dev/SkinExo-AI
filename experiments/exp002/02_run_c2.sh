#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python_binary="$project_root/.venv/bin/python"
if [[ ! -x "$python_binary" ]]; then
  printf 'Local Python environment missing: %s\n' "$python_binary" >&2
  exit 1
fi
export MPLCONFIGDIR="$project_root/data/processed/exp002/matplotlib_cache"
mkdir -p "$MPLCONFIGDIR"
"$python_binary" "$project_root/experiments/exp002/02_prepare_shared_quant.py"
bash "$project_root/experiments/exp002/02_run_r_aggregation.sh"
"$python_binary" "$project_root/experiments/exp002/02_sample_qc.py"
