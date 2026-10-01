#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export MPLCONFIGDIR="$project_root/data/processed/exp003/matplotlib_cache"
"$project_root/.venv/bin/python" "$project_root/experiments/exp003/03_prepare_de_input.py"
bash "$project_root/experiments/exp003/03_run_r.sh"
"$project_root/.venv/bin/python" "$project_root/experiments/exp003/03_c3_artifacts.py"
