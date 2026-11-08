#!/usr/bin/env python3
"""Create a GitHub repository via the REST API.

The token is resolved from the GH_TOKEN environment variable first, then from
the local git credential store (`git credential fill`) — the same place
`git push` gets it. Nothing is hardcoded.

Examples:
    python gh_create.py --name my-repo --description "One line about it"
    python gh_create.py --name my-repo --public --description "OSS release"
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def gh_token() -> str:
    """Token from GH_TOKEN, or from the local git credential store."""
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
    raise SystemExit("No GitHub token found: set GH_TOKEN or run `git push` once to store credentials.")


def api(method: str, path: str, payload: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={
            "Authorization": f"token {gh_token()}",
            "User-Agent": "gh-repo-kit",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        raise SystemExit(f"GitHub API {method} {path} -> HTTP {e.code}\n{body}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a GitHub repository.")
    parser.add_argument("--name", required=True, help="repository name")
    parser.add_argument("--description", default="", help="short description")
    parser.add_argument("--private", action="store_true", help="create a private repo (default)")
    parser.add_argument("--public", action="store_true", help="create a public repo")
    parser.add_argument("--homepage", default="", help="project homepage URL")
    visibility_private = True
    args = parser.parse_args()
    if args.public:
        visibility_private = False
    elif args.private:
        visibility_private = True

    data = api("POST", "/user/repos", {
        "name": args.name,
        "description": args.description,
        "homepage": args.homepage,
        "private": visibility_private,
    })
    print(f"created: {data['full_name']} | private={data['private']}")
    print(f"url: {data['html_url']}")
    print(f"push: git remote add origin {data['clone_url']} && git push -u origin main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
