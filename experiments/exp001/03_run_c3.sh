#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ ! -f "$project_root/data/raw/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz" ]]; then
  printf 'Official GEO author DEG archive is required for post-DE concordance.\n' >&2
  exit 1
fi

# The R step produces independent DE results without opening the author archive.
bash "$project_root/experiments/exp001/03_run_r.sh"
"$project_root/.venv/bin/python" "$project_root/experiments/exp001/03_c3_artifacts.py"
