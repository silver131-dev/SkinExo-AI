#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
r_home="$project_root/.r-env/usr/lib/R"
r_binary="$r_home/bin/exec/R"
if [[ ! -x "$r_binary" ]]; then
  printf 'Local R executable missing: %s\n' "$r_binary" >&2
  exit 1
fi
export R_HOME="$r_home"
export R_LIBS_SITE="$r_home/site-library"
export LD_LIBRARY_PATH="$project_root/.r-env/usr/lib/x86_64-linux-gnu:$project_root/.r-env/usr/lib/x86_64-linux-gnu/blas:$project_root/.r-env/usr/lib/x86_64-linux-gnu/lapack:$r_home/lib:${LD_LIBRARY_PATH:-}"
exec "$r_binary" --slave --no-save --no-restore \
  --file="$project_root/experiments/exp002/02_aggregate_salmon.R" \
  --args "$project_root"
