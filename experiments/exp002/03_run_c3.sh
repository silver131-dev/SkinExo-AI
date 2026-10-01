#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export MPLCONFIGDIR="$project_root/data/processed/exp002/matplotlib_cache"
"$project_root/.venv/bin/python" "$project_root/experiments/exp002/03_prepare_annotation.py"
bash "$project_root/experiments/exp002/03_run_r.sh" preflight
bash "$project_root/experiments/exp002/03_run_r.sh" run
"$project_root/.venv/bin/python" "$project_root/experiments/exp002/03_c3_artifacts.py"
