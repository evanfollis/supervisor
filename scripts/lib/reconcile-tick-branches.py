#!/usr/bin/env python3
"""Build a deterministic, evidence-bearing inventory of historical tick refs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from collections import defaultdict
from pathlib import Path


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, check=check)
    return result.stdout.strip()


def patch_ids(repo: Path, commits: list[str]) -> list[str]:
    values = []
    for commit in commits:
        patch = subprocess.run(["git", "-C", str(repo), "show", "--format=", "--patch", commit],
                               text=True, capture_output=True, check=True)
        result = subprocess.run(["git", "patch-id", "--stable"], input=patch.stdout,
                                text=True, capture_output=True, check=True)
        if result.stdout.strip():
            values.append(result.stdout.split()[0])
    return sorted(set(values))


def analyze_tip(repo: Path, main: str, tip: str) -> dict:
    merge_base = git(repo, "merge-base", main, tip)
    timestamp = int(git(repo, "show", "-s", "--format=%ct", tip))
    iso = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat().replace("+00:00", "Z")
    commits = git(repo, "rev-list", "--reverse", f"{merge_base}..{tip}").splitlines()
    commit_records = []
    for commit in commits:
        commit_records.append({
            "sha": commit,
            "timestamp": int(git(repo, "show", "-s", "--format=%ct", commit)),
            "subject": git(repo, "show", "-s", "--format=%s", commit),
            "parents": git(repo, "show", "-s", "--format=%P", commit).split(),
        })
    changed = []
    for line in git(repo, "diff", "--name-status", f"{merge_base}..{tip}").splitlines():
        if not line:
            continue
        status, *paths = line.split("\t")
        changed.append({
            "status": status,
            "paths": paths,
            "paths_exist_on_main": all(Path(repo, path).exists() and
                                        subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{main}:{path}"],
                                                       capture_output=True).returncode == 0
                                        for path in paths),
        })
    left, right = git(repo, "rev-list", "--left-right", "--count", f"{main}...{tip}").split()
    non_merges = git(repo, "rev-list", "--no-merges", f"{merge_base}..{tip}").splitlines()
    return {
        "tip_sha": tip,
        "committer_timestamp": timestamp,
        "committer_time": iso,
        "merge_base_with_main": merge_base,
        "commits_from_merge_base": commit_records,
        "patch_ids": patch_ids(repo, non_merges),
        "ahead_behind_main": {"ahead": int(right), "behind": int(left)},
        "changed_paths": changed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--main", default="main")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    by_tip = {}
    by_name = defaultdict(list)
    for line in args.manifest.read_text().splitlines():
        source, ref, tip = line.split("\t")
        name = ref.removeprefix("refs/remotes/origin/").removeprefix("refs/heads/")
        by_name[name].append({"source": source, "ref": ref, "tip_sha": tip})
        if tip not in by_tip:
            by_tip[tip] = analyze_tip(args.repo, args.main, tip)

    for name in sorted(by_name):
        refs = by_name[name]
        tip = refs[0]["tip_sha"]
        local = next((r["ref"] for r in refs if r["source"] == "local"), None)
        remote = next((r["ref"] for r in refs if r["source"] == "remote-live"), None)
        tracking = next((r["ref"] for r in refs if r["source"] == "tracking"), None)
        for record in sorted(refs, key=lambda r: (r["source"], r["ref"])):
            rows.append({
                "schema_version": 1,
                "source": record["source"],
                "ref": record["ref"],
                "tick_name": name,
                "tip_sha": record["tip_sha"],
                "corresponding_refs": {"local": local, "remote_live": remote, "tracking": tracking},
                "duplicate_tip_refs": sorted(r["ref"] for r in refs if r["tip_sha"] == record["tip_sha"]),
                "analysis": by_tip[record["tip_sha"]],
                "disposition": None,
                "supporting_evidence": [],
                "resulting_commit": None,
            })

    payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": str(args.repo),
        "main_ref": args.main,
        "source_counts": {source: sum(1 for row in rows if row["source"] == source)
                           for source in ("local", "remote-live", "tracking")},
        "unique_tick_names": len(by_name),
        "unique_tip_shas": len(by_tip),
        "refs": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
