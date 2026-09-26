#!/usr/bin/env python3
"""Refresh dynamic numbers in README.md from the GitHub API.

Updates: public repo count, follower count, and star counts of the
featured-project table rows. Run with GH_TOKEN set; exits 0 always,
leaves README.md untouched when nothing changed.
"""
import os
import re
import sys
import json
import urllib.request

USER = "helloworldtang"
README = os.environ.get("README_PATH", "README.md")
TOKEN = os.environ.get("GH_TOKEN", "")


def api(path: str) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main() -> int:
    with open(README, encoding="utf-8") as f:
        text = f.read()

    user = api(f"/users/{USER}")
    repos, followers = user["public_repos"], user["followers"]

    text, n1 = re.subn(r"(Repos-)\d+(-green)", rf"\g<1>{repos}\g<2>", text)
    text, n2 = re.subn(r"(Followers-)\d+(-blue)", rf"\g<1>{followers}\g<2>", text)
    text, n3 = re.subn(r"\b\d+ Public Repos", f"{repos} Public Repos", text)
    n = n1 + n2 + n3

    # Star counts for each featured table row: | [repo](url) | NNN |
    for name in re.findall(r"\[([\w.\-]+)\]\(https://github\.com/helloworldtang/[\w.\-]+\)\s*\|\s*\d+\s*\|", text):
        stars = api(f"/repos/{USER}/{name}")["stargazers_count"]
        text, k = re.subn(
            rf"(\[\s*{re.escape(name)}\s*\]\([^)]*\)\s*\|\s*)\d+(\s*\|)",
            rf"\g<1>{stars}\g<2>",
            text,
        )
        n += k

    with open(README, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"README.md: {n} stat(s) refreshed (repos={repos}, followers={followers})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
