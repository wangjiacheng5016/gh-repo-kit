#!/usr/bin/env python3
"""Check that a list of key files actually exists in a remote GitHub repo.

Useful right after mirroring a project to GitHub: pass the paths that MUST be
present (entry points, configs, checkpoints...) and get a missing-files report
from the real remote tree — not from your local working copy.

Examples:
    python gh_verify.py --repo owner/name --branch main --files key_files.txt
    python gh_verify.py --repo owner/name -- README.md src/main.py pyproject.toml
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def gh_token() -> str | None:
    token = os.environ.get("GH_TOKEN")
    if token:
        return token
    res = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True,
    )
    for line in res.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    return None


def gh(path: str, token: str | None) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "User-Agent": "gh-repo-kit",
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"token {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def load_key_files(entries: list[str], list_file: str | None) -> list[str]:
    files = list(entries)
    if list_file:
        with open(list_file, encoding="utf-8") as f:
            files += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify key files exist in a remote GitHub repo.")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--files", help="text file with one path per line (# = comment)")
    parser.add_argument("paths", nargs="*", help="key file paths (positional)")
    args = parser.parse_args()

    key_files = load_key_files(args.paths, args.files)
    if not key_files:
        parser.error("no key files given: use --files FILE and/or positional paths")

    token = gh_token()
    repo = gh(f"/repos/{args.repo}", token)
    tree = gh(f"/repos/{args.repo}/git/trees/{args.branch}?recursive=1", token)
    remote = {t["path"] for t in tree["tree"] if t["type"] == "blob"}

    print(f"repo: {repo['full_name']} | private={repo['private']} "
          f"| default_branch={repo['default_branch']}")
    print(f"remote file count: {len(remote)} | truncated flag: {tree.get('truncated', False)}")

    missing = [p for p in key_files if p not in remote]
    if missing:
        print(f"key files: MISSING {len(missing)}/{len(key_files)}")
        for p in missing:
            print(f"  - {p}")
        return 2
    print(f"key files present: ALL OK ({len(key_files)}/{len(key_files)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
