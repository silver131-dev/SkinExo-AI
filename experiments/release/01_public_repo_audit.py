#!/usr/bin/env python3
"""Audit the current Git tree and reachable history for public-release risks.

The output contains file paths and risk categories only. Matched content is
never written to stdout or to the JSON report.
"""

from __future__ import annotations

import json
import argparse
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/release/public_github_v1_audit.json"
TEN_MB = 10 * 1024 * 1024
FIFTY_MB = 50 * 1024 * 1024
CONTENT_SCAN_EXCLUSIONS = {
    "experiments/release/01_public_repo_audit.py",
    "outputs/release/public_github_v1_audit.json",
    "reports/PUBLIC_GITHUB_V1_readiness.md",
    "docs/release/PUBLIC_V1_MANIFEST.md",
}

SECRET_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"(?:ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "bearer_token": re.compile(rb"Authorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I),
    "credential_assignment": re.compile(
        rb"(?:password|passwd|api[_-]?key|client[_-]?secret)\s*[:=]\s*['\"][^'\"\r\n]{6,}['\"]",
        re.I,
    ),
}
EMAIL = re.compile(rb"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
ABSOLUTE_PATH = re.compile(rb"(?:/home/[^/\s]+/|/Users/[^/\s]+/|[A-Za-z]:\\Users\\[^\\\s]+\\)")
REGISTRATION = re.compile(rb"(?:registration[-_ ]form|whatsapp)", re.I)
INSTITUTIONAL_AUTH = re.compile(
    rb"institutional.{0,80}(?:login|credential|password|cookie|token|authentication)",
    re.I | re.S,
)


def git(*args: str, input_data: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_data, check=True, capture_output=True
    ).stdout


def revision_args(scope: str) -> list[str]:
    if scope == "all":
        return ["--all"]
    if scope == "head":
        return ["HEAD"]
    raise ValueError(f"Unsupported history scope: {scope}")


def reachable_blobs(scope: str) -> dict[str, set[str]]:
    paths_by_oid: dict[str, set[str]] = defaultdict(set)
    if scope == "index":
        for line in git("ls-files", "--stage").decode().splitlines():
            metadata, path = line.split("\t", 1)
            oid = metadata.split()[1]
            paths_by_oid[oid].add(path)
        return paths_by_oid
    for line in git("rev-list", "--objects", *revision_args(scope)).decode().splitlines():
        oid, _, path = line.partition(" ")
        if path:
            paths_by_oid[oid].add(path)
    return paths_by_oid


def blob_sizes(oids: list[str]) -> dict[str, int]:
    payload = ("\n".join(oids) + "\n").encode()
    rows = git("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)", input_data=payload)
    sizes = {}
    for row in rows.decode().splitlines():
        oid, object_type, size = row.split()
        if object_type == "blob":
            sizes[oid] = int(size)
    return sizes


def current_files() -> list[str]:
    candidates = git("ls-files", "--cached", "--others", "--exclude-standard").decode().splitlines()
    return sorted(path for path in candidates if (ROOT / path).is_file())


def classify_path(path: str) -> set[str]:
    lower = path.lower()
    categories = set()
    if lower.endswith(".pdf"):
        categories.add("licensed_or_publication_pdf")
    if lower.startswith("data/raw/") or re.search(r"\.(?:fastq|fq)(?:\.gz)?$|\.(?:bam|cram|sra)$|raw\.tar$", lower):
        categories.add("raw_omics")
    if re.search(r"(?:gene_count|total_count|counts_matrix|quant\.sf)(?:\.|$)", lower):
        categories.add("processed_input_matrix")
    if any(part in lower for part in ("institutional_access", "academic_network_harvest")):
        categories.add("institutional_workflow_note")
    if lower.endswith((".swp", ".tmp", ".part", ".pyc", ".ds_store")) or "__pycache__/" in lower:
        categories.add("temporary_or_editor_file")
    return categories


def scan_blobs(paths_by_oid: dict[str, set[str]], sizes: dict[str, int]) -> dict[str, list[str]]:
    findings: dict[str, set[str]] = defaultdict(set)
    for oid, paths in paths_by_oid.items():
        size = sizes.get(oid)
        if size is None:
            continue
        for path in paths:
            for category in classify_path(path):
                findings[category].add(path)
        if size > TEN_MB:
            continue
        scan_paths = paths - CONTENT_SCAN_EXCLUSIONS
        if not scan_paths:
            continue
        data = git("cat-file", "blob", oid)
        if b"\x00" in data:
            continue
        for category, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                findings[f"secret:{category}"].update(scan_paths)
        emails = {match.group(0).lower() for match in EMAIL.finditer(data)}
        if any(not email.endswith(b"@users.noreply.github.com") for email in emails):
            findings["email_address"].update(scan_paths)
        if ABSOLUTE_PATH.search(data):
            findings["absolute_machine_path"].update(scan_paths)
        if REGISTRATION.search(data):
            findings["registration_or_phone_channel"].update(
                path for path in scan_paths if not path.startswith("docs/compliance/")
            )
        if INSTITUTIONAL_AUTH.search(data):
            findings["institutional_authentication"].update(
                path for path in scan_paths if not path.startswith("docs/compliance/")
            )
    return {key: sorted(value) for key, value in sorted(findings.items()) if value}


def scan_worktree(paths: list[str]) -> dict[str, list[str]]:
    findings: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        if path in CONTENT_SCAN_EXCLUSIONS:
            continue
        source = ROOT / path
        if source.stat().st_size > TEN_MB:
            continue
        data = source.read_bytes()
        if b"\x00" in data:
            continue
        for category, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                findings[f"secret:{category}"].add(path)
        emails = {match.group(0).lower() for match in EMAIL.finditer(data)}
        if any(not email.endswith(b"@users.noreply.github.com") for email in emails):
            findings["email_address"].add(path)
        if ABSOLUTE_PATH.search(data):
            findings["absolute_machine_path"].add(path)
        if REGISTRATION.search(data) and not path.startswith("docs/compliance/"):
            findings["registration_or_phone_channel"].add(path)
        if INSTITUTIONAL_AUTH.search(data) and not path.startswith("docs/compliance/"):
            findings["institutional_authentication"].add(path)
    return {key: sorted(value) for key, value in sorted(findings.items())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-scope", choices=("all", "head", "index"), default="all")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    paths_by_oid = reachable_blobs(args.history_scope)
    sizes = blob_sizes(list(paths_by_oid))
    history_findings = scan_blobs(paths_by_oid, sizes)
    tracked = current_files()
    current_findings: dict[str, list[str]] = defaultdict(list)
    for path in tracked:
        for category in classify_path(path):
            current_findings[category].append(path)

    largest_history = sorted(
        (
            {"bytes": sizes[oid], "paths": sorted(paths)}
            for oid, paths in paths_by_oid.items()
            if oid in sizes
        ),
        key=lambda row: row["bytes"],
        reverse=True,
    )[:20]
    required = [
        "data/metadata/skinexo_component_universe.csv",
        "data/metadata/skinexo_context_features.csv",
        "data/metadata/skinexo_contexts.csv",
        "data/metadata/skinexo_response_atlas_long.csv",
        "data/metadata/skinexo_axis_summary.csv",
        "data/metadata/skinexo_phenotype_anchors.csv",
        "data/metadata/skinexo_reliability.csv",
        "outputs/framework/framework_f2_atlas.json",
        "outputs/framework/framework_f2_validation.json",
        "outputs/retrieval/retrieval_r1.json",
    ]
    tracked_set = set(tracked)
    authors = []
    commit_count = 0
    if args.history_scope != "index":
        revision = "--all" if args.history_scope == "all" else "HEAD"
        authors = sorted(set(git("log", revision, "--format=%ae").decode().splitlines()))
        commit_count = int(git("rev-list", revision, "--count").decode().strip())
    report = {
        "source_checkpoint": "DEV-C2",
        "source_commit": "afcf6dd1c81520bbfdcad333f7f01ab6b9c3089b",
        "history_scope": args.history_scope.upper(),
        "commits_audited": commit_count,
        "tracked_file_count": len(tracked),
        "reachable_blob_count": len(sizes),
        "current_path_findings": {key: sorted(value) for key, value in sorted(current_findings.items())},
        "current_content_findings": scan_worktree(tracked),
        "history_findings": history_findings,
        "files_over_10_mb_current": sorted(
            path for path in tracked if (ROOT / path).is_file() and (ROOT / path).stat().st_size > TEN_MB
        ),
        "files_over_50_mb_current": sorted(
            path for path in tracked if (ROOT / path).is_file() and (ROOT / path).stat().st_size > FIFTY_MB
        ),
        "blobs_over_10_mb_history": [row for row in largest_history if row["bytes"] > TEN_MB],
        "blobs_over_50_mb_history": [row for row in largest_history if row["bytes"] > FIFTY_MB],
        "largest_history_blobs": largest_history,
        "commit_author_emails": {
            "count": len(authors),
            "all_github_noreply": bool(authors) and all(email.endswith("@users.noreply.github.com") for email in authors),
        },
        "explorer_required_artifacts": {
            "required": required,
            "all_tracked": all(path in tracked_set for path in required),
            "missing": [path for path in required if path not in tracked_set],
        },
    }
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
