#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export MPLCONFIGDIR="$project_root/data/processed/exp003/matplotlib_c4_cache"
"$project_root/.venv/bin/python" "$project_root/experiments/exp003/04_run_enrichment.py"
"$project_root/.venv/bin/python" "$project_root/experiments/exp003/04_finalize_third_context.py"
"$project_root/.venv/bin/python" "$project_root/experiments/framework/01_validate_framework.py"
