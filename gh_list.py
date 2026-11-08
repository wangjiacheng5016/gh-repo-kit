#!/usr/bin/env python3
"""List repositories of a GitHub user with private flag and last-update date.

Examples:
    python gh_list.py                 # authenticated user (shows private repos too)
    python gh_list.py --user octocat  # any public account
"""

import argparse
import json
import os
import subprocess
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


def fetch(user: str | None, token: str | None):
    """Yield all repos, following pagination."""
    page = 1
    while True:
        url = f"{API}/users/{user}/repos" if user else f"{API}/user/repos?affiliation=owner"
        sep = "&" if "?" in url else "?"
        req = urllib.request.Request(
            f"{url}{sep}per_page=100&page={page}&sort=updated",
            headers={
                "User-Agent": "gh-repo-kit",
                "Accept": "application/vnd.github+json",
                **({"Authorization": f"token {token}"} if token else {}),
            },
        )
        batch = json.load(urllib.request.urlopen(req))
        if not batch:
            return
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="List GitHub repositories.")
    parser.add_argument("--user", help="GitHub login (omit for the authenticated user)")
    args = parser.parse_args()

    token = gh_token() if not args.user else None
    repos = list(fetch(args.user, token))
    print(f"account: {args.user or 'authenticated user'} | repos: {len(repos)}")
    for r in repos:
        print(f"  {r['name']:<45} private={str(r['private']):<5} "
              f"updated={r['updated_at'][:10]} {(r.get('description') or '')[:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
